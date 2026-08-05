import { execFileSync } from 'node:child_process'
import { defineConfig } from 'cypress'

function mysqlExec(sql: string) {
  execFileSync(
    'docker',
    [
      'exec',
      'fast-full-stack-mysql',
      'mysql',
      '-uroot',
      '-pFastFullStack123',
      'full-stack-demo',
      '-e',
      sql
    ],
    { stdio: 'pipe' }
  )
  return null
}

function redisKeys(pattern: string) {
  const output = execFileSync(
    'docker',
    ['exec', 'fast-full-stack-redis', 'redis-cli', '-a', 'FastFullStackRedis123', '--raw', 'KEYS', pattern],
    { stdio: 'pipe', encoding: 'utf8' }
  )
  return output.split(/\r?\n/).map(key => key.trim()).filter(Boolean)
}

function redisDel(keys: string[]) {
  if (keys.length === 0) return null
  execFileSync(
    'docker',
    ['exec', 'fast-full-stack-redis', 'redis-cli', '-a', 'FastFullStackRedis123', 'DEL', ...keys],
    { stdio: 'pipe' }
  )
  return null
}

function redisSetEx(key: string, value: string, seconds: number) {
  execFileSync(
    'docker',
    ['exec', 'fast-full-stack-redis', 'redis-cli', '-a', 'FastFullStackRedis123', 'SET', key, value, 'EX', String(seconds)],
    { stdio: 'pipe' }
  )
  return null
}

function e2EClientIp(runId: string) {
  const suffix = String(runId).replace(/[^0-9]/g, '')
  return `10.252.${Number(suffix.slice(-4, -2)) || 1}.${Number(suffix.slice(-2)) || 1}`
}

function prepareE2ERateLimit(runId: string) {
  redisSetEx(`rate_limit:whitelist:${e2EClientIp(runId)}`, '1', 600)
  return null
}

function cleanupE2ERateLimit(runId: string) {
  const suffix = String(runId).replace(/[^0-9]/g, '')
  const clientIp = e2EClientIp(suffix)
  redisDel([
    `rate_limit:ip:${clientIp}`,
    ...redisKeys(`rate_limit:ip_user:${clientIp}_*`)
  ])
  redisDel([
    `rate_limit:whitelist:${clientIp}`,
    `rate_limit:whitelist:10.250.${Number(suffix.slice(-4, -2)) || 1}.${Number(suffix.slice(-2)) || 1}`,
    `rate_limit:blacklist:10.251.${Number(suffix.slice(-4, -2)) || 1}.${Number(suffix.slice(-2)) || 1}`
  ])
  return null
}

export default defineConfig({
  e2e: {
    specPattern: 'cypress/e2e/**/*.{cy,spec}.{js,jsx,ts,tsx}',
    baseUrl: 'http://localhost:5173',
    supportFile: 'cypress/support/e2e.ts',
    setupNodeEvents(on) {
      on('task', {
        cleanupE2EData(runId: string) {
          const suffix = String(runId).replace(/[^0-9]/g, '')
          const sql = `
            DELETE ur FROM sys_user_roles ur
            JOIN sys_users u ON u.id = ur.user_id
            WHERE u.user_name IN ('e2e_front_${suffix}', 'e2e_admin_${suffix}');

            DELETE rp FROM sys_role_permissions rp
            JOIN sys_roles r ON r.id = rp.role_id
            WHERE r.role_code = 'ROLE_E2E_${suffix}';

            DELETE rm FROM sys_role_menus rm
            JOIN sys_roles r ON r.id = rm.role_id
            WHERE r.role_code = 'ROLE_E2E_${suffix}';

            DELETE FROM sys_api_permissions
            WHERE path_pattern = '/e2e/${suffix}' OR permission_code = 'E2E_PERMISSION_${suffix}';

            DELETE FROM sys_menus
            WHERE menu_code = 'E2E_MENU_${suffix}';

            DELETE FROM sys_permissions
            WHERE permission_code = 'E2E_PERMISSION_${suffix}';

            DELETE FROM sys_roles
            WHERE role_code = 'ROLE_E2E_${suffix}';

            DELETE FROM sys_users
            WHERE user_name IN ('e2e_front_${suffix}', 'e2e_admin_${suffix}');
          `
          cleanupE2ERateLimit(suffix)
          return mysqlExec(sql)
        },
        prepareE2ERateLimit(runId: string) {
          return prepareE2ERateLimit(runId)
        },
        resetE2ERateLimit(runId: string) {
          return cleanupE2ERateLimit(runId)
        }
      })
    },
  },
})
