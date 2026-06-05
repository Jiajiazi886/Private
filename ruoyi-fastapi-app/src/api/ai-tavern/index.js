import request from "@/utils/request";

export function listCharacters(params) {
  return request({
    url: "/ai/tavern/characters",
    method: "get",
    params,
  });
}

export function addCharacter(data) {
  return request({
    url: "/ai/tavern/characters",
    method: "post",
    data,
  });
}

export function createConversation(data) {
  return request({
    url: "/ai/tavern/conversations",
    method: "post",
    data,
  });
}

export function listConversations(params) {
  return request({
    url: "/ai/tavern/conversations",
    method: "get",
    params,
  });
}

export function listMessages(conversationId) {
  return request({
    url: `/ai/tavern/conversations/${conversationId}/messages`,
    method: "get",
  });
}

export function sendChat(data) {
  return request({
    url: "/ai/tavern/chat/send",
    method: "post",
    data,
    timeout: 60000,
  });
}
