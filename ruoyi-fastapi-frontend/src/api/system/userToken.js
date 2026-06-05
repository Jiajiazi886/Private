import request from '@/utils/request'

export function listUserTokenSetting(query) {
  return request({
    url: '/system/user-token-setting/list',
    method: 'get',
    params: query
  })
}

export function updateUserTokenSetting(data) {
  return request({
    url: '/system/user-token-setting',
    method: 'put',
    data
  })
}
