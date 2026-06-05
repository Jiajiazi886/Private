import request from "@/utils/request";

export function getTavernDashboard() {
  return request({
    url: "/admin/ai/tavern/dashboard",
    method: "get",
  });
}

export function listTokenUsage(params) {
  return request({
    url: "/admin/ai/tavern/token-usage",
    method: "get",
    params,
  });
}
