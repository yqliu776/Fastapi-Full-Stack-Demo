// 菜单接口定义

export interface Menu {
  id: number;
  menu_name: string;
  menu_code: string;
  menu_path: string;
  component_key?: string;
  parent_id?: number;
  sort_order: number;
  delete_flag?: string; // 删除标识，N正常/Y已软删除
  creation_date: string;
  last_update_date: string;
  children?: Menu[];
}

export interface MenuCreate {
  menu_name: string;
  menu_code: string;
  menu_path: string;
  component_key?: string;
  parent_id?: number;
  sort_order?: number;
  created_by: string;
  last_updated_by: string;
  last_update_login: string;
}

export interface MenuUpdate {
  menu_name?: string;
  menu_path?: string;
  component_key?: string;
  parent_id?: number;
  sort_order?: number;
  last_updated_by: string;
  last_update_login: string;
}
