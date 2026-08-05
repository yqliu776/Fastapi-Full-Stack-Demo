/// <reference types="cypress" />

type NetworkEntry = {
  test: string;
  method: string;
  path: string;
  status?: number;
  requestBody?: unknown;
  responseCode?: number;
  responseMessage?: string;
};

const apiBase = Cypress.env('apiBaseUrl') || 'http://localhost:8090';
const runId = String(Cypress.env('RUN_ID') || Date.now()).replace(/\D/g, '').slice(-10);
const reportPath = `cypress/reports/full-system-network-${runId}.json`;

const data = {
  frontUser: `e2e_front_${runId}`,
  frontPassword: 'E2ePass123',
  adminUser: `e2e_admin_${runId}`,
  adminPassword: 'E2ePass123',
  roleName: `E2E角色${runId}`,
  roleNameUpdated: `E2E角色更新${runId}`,
  roleCode: `ROLE_E2E_${runId}`,
  permissionName: `E2E权限${runId}`,
  permissionNameUpdated: `E2E权限更新${runId}`,
  permissionCode: `E2E_PERMISSION_${runId}`,
  apiPath: `/e2e/${runId}`,
  menuName: `E2E菜单${runId}`,
  menuNameUpdated: `E2E菜单更新${runId}`,
  menuCode: `E2E_MENU_${runId}`,
  menuPath: `/system/e2e-${runId}`,
  menuPathUpdated: `/system/e2e-${runId}-updated`,
  clientIp: `10.252.${Number(runId.slice(-4, -2)) || 1}.${Number(runId.slice(-2)) || 1}`,
  whitelistId: `10.250.${Number(runId.slice(-4, -2)) || 1}.${Number(runId.slice(-2)) || 1}`,
  blacklistId: `10.251.${Number(runId.slice(-4, -2)) || 1}.${Number(runId.slice(-2)) || 1}`
};

const networkLog: NetworkEntry[] = [];
let activeTest = '';

function installNetworkLogger() {
  cy.intercept({ url: `${apiBase}/**`, middleware: true }, (req) => {
    req.headers['x-forwarded-for'] = data.clientIp;
    req.headers['x-real-ip'] = data.clientIp;
    const requestBody = Cypress._.cloneDeep(req.body);
    const url = new URL(req.url);
    const alias = getApiAlias(req.method, url.pathname);
    if (alias) {
      req.alias = alias;
    }
    req.continue((res) => {
      const responseBody = res.body as any;
      networkLog.push({
        test: activeTest,
        method: req.method,
        path: `${url.pathname}${url.search}`,
        status: res.statusCode,
        requestBody,
        responseCode: responseBody?.code,
        responseMessage: responseBody?.message
      });
    });
  });
}

function getApiAlias(method: string, path: string) {
  const route = `${method.toUpperCase()} ${path}`;
  if (route === 'POST /users/register') return 'frontRegister';
  if (route === 'POST /auth/login') {
    return activeTest.includes('front guest') ? 'frontLogin' : 'adminLogin';
  }
  if (route === 'GET /auth/me') return activeTest.includes('front guest') ? 'frontMe' : 'adminMe';
  if (route === 'GET /menus/current/tree') return 'adminMenuTree';
  if (route === 'GET /users/list') return 'usersList';
  if (route === 'GET /roles') return 'rolesList';
  if (route === 'GET /permissions') return 'permissionsList';
  if (route === 'GET /permissions/api-bindings') return 'apiBindingsList';
  if (route === 'GET /menus') return 'menusList';
  if (route === 'POST /users/admin/create') return 'createUser';
  if (route.startsWith('PUT /users/update/')) return 'updateUser';
  if (route.startsWith('POST /users/reset-password/')) return 'resetPassword';
  if (route.startsWith('POST /users/assign-roles/')) return 'assignAdminRoles';
  if (route === 'POST /roles') return 'createRole';
  if (/^PUT \/roles\/\d+$/.test(route)) return 'updateRole';
  if (/^PUT \/roles\/\d+\/permissions$/.test(route)) return 'replacePermissions';
  if (/^PUT \/roles\/\d+\/menus$/.test(route)) return 'replaceMenus';
  if (route.startsWith('DELETE /roles/')) return 'deleteRole';
  if (route === 'POST /permissions') return 'createPermission';
  if (/^PUT \/permissions\/\d+$/.test(route)) return 'updatePermission';
  if (route === 'POST /permissions/api-bindings') return 'createApiBinding';
  if (route.startsWith('PUT /permissions/api-bindings/')) return 'updateApiBinding';
  if (route.startsWith('DELETE /permissions/api-bindings/')) return 'deleteApiBinding';
  if (route === 'POST /menus') return 'createMenu';
  if (/^PUT \/menus\/\d+$/.test(route)) return 'updateMenu';
  if (route.startsWith('DELETE /menus/')) return 'deleteMenu';
  if (route === 'GET /rate-limit/stats') return 'rateStats';
  if (route === 'POST /rate-limit/whitelist') return 'addWhitelist';
  if (route === 'POST /rate-limit/blacklist') return 'addBlacklist';
  return undefined;
}

function visibleDialog() {
  return cy.get('.el-dialog:visible').last();
}

function inputByPlaceholder(placeholder: string) {
  return cy.get(`input[placeholder="${placeholder}"]`).filter(':visible').first();
}

function clearAndType(placeholder: string, value: string) {
  inputByPlaceholder(placeholder).clear().type(value);
}

function clickVisibleButton(label: string) {
  cy.contains('button:visible', label).click();
}

function ensureRoleSelected(roleCode: string) {
  cy.contains('.role-card', roleCode).then(($card) => {
    if (!$card.hasClass('is-assigned') && !$card.hasClass('is-selected-new')) {
      cy.wrap($card).click();
    }
  });
}

function ensureRoleRemoved(roleCode: string) {
  cy.contains('.role-card', roleCode).then(($card) => {
    if (!$card.hasClass('is-removing')) {
      cy.wrap($card).click();
    }
  });
}

function confirmDialog(label = '确定') {
  cy.get('.el-message-box:visible').last().within(() => {
    cy.contains('button', label).click();
  });
}

function tableRow(text: string) {
  return cy.contains('.el-table__body-wrapper tr', text, { timeout: 12000 });
}

function loginAdminByPage() {
  cy.session('admin-page-login', () => {
    cy.visit('/admin-console/login');
    cy.intercept('POST', `${apiBase}/auth/login`).as('adminLogin');
    cy.intercept('GET', `${apiBase}/menus/current/tree`).as('adminMenuTree');
    clearAndType('用户名', 'admin');
    clearAndType('密码', 'Admin@123');
    clickVisibleButton('登 录');
    cy.wait('@adminLogin').its('response.statusCode').should('eq', 200);
    cy.wait('@adminMenuTree').its('response.statusCode').should('eq', 200);
    cy.location('pathname', { timeout: 15000 }).should('eq', '/admin-console/dashboard');
  }, {
    validate() {
      cy.getCookie('access_token').should('exist');
    }
  });
  cy.visit('/admin-console/dashboard');
  cy.location('pathname', { timeout: 15000 }).should('eq', '/admin-console/dashboard');
}

function visitAdmin(path: string, heading: string) {
  cy.visit(path);
  cy.contains(heading, { timeout: 15000 }).should('be.visible');
  const pageAliases: Record<string, string[]> = {
    '/admin-console/system/user': ['@usersList', '@rolesList'],
    '/admin-console/system/role': ['@rolesList'],
    '/admin-console/system/permission': ['@permissionsList', '@apiBindingsList'],
    '/admin-console/system/menu': ['@menusList']
  };
  (pageAliases[path] || []).forEach((alias) => {
    cy.wait(alias).its('response.statusCode').should('eq', 200);
  });
}

function searchByPlaceholder(placeholder: string, value: string) {
  clearAndType(placeholder, value);
  clickVisibleButton('搜索');
}

function assertNo5xxForCurrentTest() {
  cy.then(() => {
    const failed = networkLog.filter((entry) => entry.test === activeTest && (entry.status || 0) >= 500);
    expect(failed, `no 5xx API responses in ${activeTest}`).to.deep.equal([]);
  });
}

describe('full frontend system flow', () => {
  before(() => {
    cy.task('resetE2ERateLimit', runId);
    cy.task('prepareE2ERateLimit', runId);
    cy.task('cleanupE2EData', runId);
    cy.task('prepareE2ERateLimit', runId);
  });

  beforeEach(function () {
    activeTest = this.currentTest?.fullTitle() || '';
    cy.clearCookies();
    cy.clearLocalStorage();
    installNetworkLogger();
  });

  afterEach(() => {
    assertNo5xxForCurrentTest();
  });

  after(() => {
    cy.writeFile(reportPath, networkLog);
    cy.task('cleanupE2EData', runId);
  });

  it('covers front guest pages, registration, login, user center, and logout', () => {
    cy.visit('/');
    cy.contains('FastAPI × Vue 3 × Element Plus').should('be.visible');
    clickVisibleButton('前台登录');
    cy.location('pathname').should('eq', '/login');

    cy.visit('/user');
    cy.location('pathname').should('eq', '/login');

    cy.visit('/register');
    cy.contains('创建账号').should('be.visible');
    cy.intercept('POST', `${apiBase}/users/register`).as('frontRegister');
    clearAndType('用户名（仅允许字母、数字和下划线）', data.frontUser);
    clearAndType('邮箱', `${data.frontUser}@example.com`);
    clearAndType('手机号', `138${runId.padStart(8, '0').slice(-8)}`);
    clearAndType('密码（至少6个字符）', data.frontPassword);
    clearAndType('确认密码', data.frontPassword);
    clickVisibleButton('注 册');
    cy.wait('@frontRegister').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(200);
      expect(request.body).to.not.have.property('role_codes');
      expect(request.body).to.include({
        user_name: data.frontUser,
        password: data.frontPassword
      });
    });

    cy.location('pathname', { timeout: 5000 }).should('eq', '/login');
    cy.contains('注册成功，请登录').should('be.visible');

    cy.intercept('POST', `${apiBase}/auth/login`).as('frontLogin');
    cy.intercept('GET', `${apiBase}/auth/me`).as('frontMe');
    clearAndType('密码', data.frontPassword);
    clickVisibleButton('登 录');
    cy.wait('@frontLogin').its('response.statusCode').should('eq', 200);
    cy.wait('@frontMe').its('response.statusCode').should('eq', 200);
    cy.location('pathname', { timeout: 10000 }).should('eq', '/user');
    cy.contains(data.frontUser).should('be.visible');
    cy.contains('账号角色').should('be.visible');

    clickVisibleButton('退出');
    confirmDialog();
    cy.location('pathname', { timeout: 10000 }).should('eq', '/');
  });

  it('covers admin login, dynamic menu loading, and all main admin pages', () => {
    loginAdminByPage();
    cy.contains('控制台').should('be.visible');
    cy.contains('系统管理').should('be.visible');

    [
      ['/admin-console/system/user', '用户管理'],
      ['/admin-console/system/role', '角色管理'],
      ['/admin-console/system/permission', '权限管理'],
      ['/admin-console/system/menu', '菜单管理'],
      ['/admin-console/system/api-rate-limit', 'API限流管理'],
      ['/admin-console/system/swagger-ui', 'API 文档'],
      ['/admin-console/dashboard/profile', '个人信息']
    ].forEach(([path, heading]) => {
      visitAdmin(path, heading);
    });
  });

  it('covers user create/edit/password and protects admin super role assignment', () => {
    loginAdminByPage();
    visitAdmin('/admin-console/system/user', '用户管理');

    cy.intercept('POST', `${apiBase}/users/admin/create`).as('createUser');
    clickVisibleButton('创建用户');
    visibleDialog().within(() => {
      clearAndType('请输入用户名', data.adminUser);
      clearAndType('请输入邮箱', `${data.adminUser}@example.com`);
      clearAndType('请输入电话', `139${runId.padStart(8, '0').slice(-8)}`);
      clearAndType('请输入密码', data.adminPassword);
      cy.contains('button', '确认创建').click();
    });
    cy.wait('@createUser').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(200);
      expect(request.body.role_codes).to.deep.eq(['ROLE_USER']);
    });

    searchByPlaceholder('请输入用户名', data.adminUser);
    tableRow(data.adminUser).should('be.visible');

    cy.intercept('PUT', `${apiBase}/users/update/*`).as('updateUser');
    tableRow(data.adminUser).within(() => cy.contains('button', '编辑').click());
    visibleDialog().within(() => {
      clearAndType('请输入邮箱', `${data.adminUser}.updated@example.com`);
      clearAndType('请输入电话', `137${runId.padStart(8, '0').slice(-8)}`);
      cy.contains('button', '保存修改').click();
    });
    cy.wait('@updateUser').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(200);
      expect(request.body).to.not.have.property('role_codes');
      expect(request.body).to.not.have.property('password');
      expect(request.body.delete_flag).to.eq('N');
    });

    cy.intercept('POST', `${apiBase}/users/reset-password/*`).as('resetPassword');
    tableRow(data.adminUser).within(() => cy.contains('button', '密码').click());
    visibleDialog().within(() => {
      clearAndType('请输入新密码', `${data.adminPassword}x`);
      clearAndType('请再次输入新密码', `${data.adminPassword}x`);
      cy.contains('button', '确认修改').click();
    });
    cy.wait('@resetPassword').its('response.statusCode').should('eq', 200);

    searchByPlaceholder('请输入用户名', 'admin');
    cy.intercept('POST', `${apiBase}/users/assign-roles/*`).as('assignAdminRoles');
    tableRow('admin').within(() => cy.contains('button', '角色').click());
    visibleDialog().within(() => {
      ensureRoleSelected('ROLE_USER');
      ensureRoleRemoved('ROLE_SUPER_ADMIN');
      cy.contains('button', '保存更改').click();
    });
    cy.wait('@assignAdminRoles').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(400);
      expect(request.body.role_codes).to.not.include('ROLE_SUPER_ADMIN');
      expect(request.body.role_codes).to.include('ROLE_USER');
    });
  });

  it('covers role CRUD, role permission replacement, and role menu replacement', () => {
    loginAdminByPage();
    visitAdmin('/admin-console/system/role', '角色管理');

    cy.intercept('POST', `${apiBase}/roles`).as('createRole');
    clickVisibleButton('创建角色');
    visibleDialog().within(() => {
      clearAndType('请输入角色名称', data.roleName);
      clearAndType('请输入角色代码（如 ROLE_ADMIN）', data.roleCode);
      cy.contains('button', '确认创建').click();
    });
    cy.wait('@createRole').its('response.statusCode').should('eq', 200);

    searchByPlaceholder('请输入角色代码', data.roleCode);
    tableRow(data.roleCode).should('be.visible');

    cy.intercept('PUT', `${apiBase}/roles/*`).as('updateRole');
    tableRow(data.roleCode).within(() => cy.contains('button', '编辑').click());
    visibleDialog().within(() => {
      clearAndType('请输入角色名称', data.roleNameUpdated);
      cy.contains('button', '保存修改').click();
    });
    cy.wait('@updateRole').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(200);
      expect(request.body).to.not.have.property('permission_ids');
      expect(request.body).to.not.have.property('menu_ids');
    });

    cy.intercept('PUT', `${apiBase}/roles/*/permissions`).as('replacePermissions');
    tableRow(data.roleCode).within(() => cy.contains('button', '权限').click());
    visibleDialog().within(() => {
      clearAndType('搜索权限名称或代码', 'USER_MANAGE');
      cy.contains('.permission-card', 'USER_MANAGE').click();
      cy.contains('button', '保存权限').click();
    });
    cy.wait('@replacePermissions').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(200);
      expect(request.body.permission_ids).to.be.an('array').and.not.be.empty;
    });
    visibleDialog().within(() => cy.contains('button', '完成').click());

    cy.intercept('PUT', `${apiBase}/roles/*/menus`).as('replaceMenus');
    tableRow(data.roleCode).within(() => cy.contains('button', '菜单').click());
    visibleDialog().within(() => {
      clearAndType('搜索菜单名称或代码', 'USER');
      cy.contains('.menu-row', 'USER').click();
      cy.contains('button', '保存菜单').click();
    });
    cy.wait('@replaceMenus').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(200);
      expect(request.body.menu_ids).to.be.an('array').and.not.be.empty;
    });
    visibleDialog().within(() => cy.contains('button', '完成').click());

    cy.intercept('DELETE', `${apiBase}/roles/*`).as('deleteRole');
    tableRow(data.roleCode).within(() => cy.contains('button', '删除').click());
    confirmDialog('删除');
    cy.wait('@deleteRole').its('response.statusCode').should('eq', 200);
  });

  it('covers permission CRUD and API permission binding CRUD', () => {
    loginAdminByPage();
    visitAdmin('/admin-console/system/permission', '权限管理');

    cy.intercept('POST', `${apiBase}/permissions`).as('createPermission');
    clickVisibleButton('创建权限');
    visibleDialog().within(() => {
      clearAndType('请输入权限名称', data.permissionName);
      clearAndType('如 user:create', data.permissionCode);
      cy.contains('button', '确认创建').click();
    });
    cy.wait('@createPermission').its('response.statusCode').should('eq', 200);

    searchByPlaceholder('请输入权限代码', data.permissionCode);
    tableRow(data.permissionCode).should('be.visible');

    cy.intercept('PUT', `${apiBase}/permissions/*`).as('updatePermission');
    tableRow(data.permissionCode).within(() => cy.contains('button', '编辑').click());
    visibleDialog().within(() => {
      clearAndType('请输入权限名称', data.permissionNameUpdated);
      cy.contains('button', '保存修改').click();
    });
    cy.wait('@updatePermission').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(200);
      expect(request.body).to.not.have.property('role_ids');
      expect(request.body).to.not.have.property('roles');
    });

    cy.intercept('POST', `${apiBase}/permissions/api-bindings`).as('createApiBinding');
    clickVisibleButton('创建API绑定');
    visibleDialog().within(() => {
      cy.get('.el-select').eq(1).click();
    });
    cy.get('.el-select-dropdown:visible').contains(data.permissionCode).click();
    visibleDialog().within(() => {
      clearAndType('/roles/{role_id}', data.apiPath);
      clearAndType('请输入说明', `E2E API ${runId}`);
      cy.contains('button', '确认创建').click();
    });
    cy.wait('@createApiBinding').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(200);
      expect(request.body).to.include({
        method: 'GET',
        path_pattern: data.apiPath,
        permission_code: data.permissionCode
      });
    });

    clearAndType('请输入API路径', data.apiPath);
    clickVisibleButton('搜索');
    tableRow(data.apiPath).should('be.visible');

    cy.intercept('PUT', `${apiBase}/permissions/api-bindings/*`).as('updateApiBinding');
    tableRow(data.apiPath).within(() => cy.contains('button', '编辑').click());
    visibleDialog().within(() => {
      clearAndType('请输入说明', `E2E API updated ${runId}`);
      cy.contains('button', '保存修改').click();
    });
    cy.wait('@updateApiBinding').its('response.statusCode').should('eq', 200);

    cy.intercept('DELETE', `${apiBase}/permissions/api-bindings/*`).as('deleteApiBinding');
    tableRow(data.apiPath).within(() => cy.contains('button', '删除').click());
    confirmDialog('删除');
    cy.wait('@deleteApiBinding').its('response.statusCode').should('eq', 200);
  });

  it('covers menu CRUD and verifies menu update payload contract', () => {
    loginAdminByPage();
    visitAdmin('/admin-console/system/menu', '菜单管理');

    cy.intercept('POST', `${apiBase}/menus`).as('createMenu');
    clickVisibleButton('创建菜单');
    visibleDialog().within(() => {
      clearAndType('请输入菜单名称', data.menuName);
      clearAndType('请输入菜单代码', data.menuCode);
      clearAndType('如 /dashboard/profile', data.menuPath);
      cy.contains('button', '确认创建').click();
    });
    cy.wait('@createMenu').its('response.statusCode').should('eq', 200);

    searchByPlaceholder('请输入菜单名称', data.menuName);
    tableRow(data.menuCode).should('be.visible');

    cy.intercept('PUT', `${apiBase}/menus/*`).as('updateMenu');
    tableRow(data.menuCode).within(() => cy.contains('button', '编辑').click());
    visibleDialog().within(() => {
      clearAndType('请输入菜单名称', data.menuNameUpdated);
      clearAndType('如 /dashboard/profile', data.menuPathUpdated);
      cy.contains('button', '保存修改').click();
    });
    cy.wait('@updateMenu').then(({ request, response }) => {
      expect(response?.statusCode).to.eq(200);
      expect(request.body).to.not.have.property('menu_code');
      expect(request.body).to.not.have.property('created_by');
      expect(request.body.menu_path).to.eq(data.menuPathUpdated);
    });

    cy.intercept('DELETE', `${apiBase}/menus/*`).as('deleteMenu');
    tableRow(data.menuCode).within(() => cy.contains('button', '删除').click());
    confirmDialog('删除');
    cy.wait('@deleteMenu').its('response.statusCode').should('eq', 200);
  });

  it('covers rate limit management and swagger page network availability', () => {
    loginAdminByPage();
    visitAdmin('/admin-console/system/api-rate-limit', 'API限流管理');

    cy.intercept('GET', `${apiBase}/rate-limit/stats*`).as('rateStats');
    cy.contains('.page-card', '限流状态检查').scrollIntoView().within(() => {
      cy.get('input[placeholder="IP地址或用户ID"]').clear().type(data.whitelistId);
      cy.contains('button', '检查限流状态').click();
    });
    cy.wait('@rateStats').its('response.statusCode').should('eq', 200);
    cy.contains('检查结果').should('be.visible');

    cy.intercept('POST', `${apiBase}/rate-limit/whitelist`).as('addWhitelist');
    cy.contains('.el-tabs__item', '白名单').click();
    cy.contains('.tab-pane', '添加白名单').within(() => {
      cy.get('input[placeholder="IP地址或用户ID"]').clear().type(data.whitelistId);
      cy.contains('button', '添加到白名单').click();
    });
    cy.wait('@addWhitelist').its('response.statusCode').should('eq', 200);

    cy.intercept('POST', `${apiBase}/rate-limit/blacklist`).as('addBlacklist');
    cy.contains('.el-tabs__item', '黑名单').click();
    cy.contains('.tab-pane', '添加黑名单').within(() => {
      cy.get('input[placeholder="IP地址或用户ID"]').clear().type(data.blacklistId);
      cy.contains('button', '添加到黑名单').click();
    });
    cy.wait('@addBlacklist').its('response.statusCode').should('eq', 200);

    visitAdmin('/admin-console/system/swagger-ui', 'API 文档');
    cy.get('iframe.swagger-iframe', { timeout: 15000 })
      .should('have.attr', 'src')
      .and('include', '/api/docs');
  });
});
