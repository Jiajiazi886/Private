import request from "@/utils/request";

export function listCharacters(params) {
  return request({
    url: "/ai/tavern/characters",
    method: "get",
    params,
  });
}

export function getCharacter(id) {
  return request({
    url: `/ai/tavern/characters/${id}`,
    method: "get",
  });
}

export function addCharacter(data) {
  return request({
    url: "/ai/tavern/characters",
    method: "post",
    data,
  });
}

export function updateCharacter(id, data) {
  return request({
    url: `/ai/tavern/characters/${id}`,
    method: "put",
    data,
  });
}

export function delCharacter(id) {
  return request({
    url: `/ai/tavern/characters/${id}`,
    method: "delete",
  });
}

export function listConversations(params) {
  return request({
    url: "/ai/tavern/conversations",
    method: "get",
    params,
  });
}

export function createConversation(data) {
  return request({
    url: "/ai/tavern/conversations",
    method: "post",
    data,
  });
}

export function getConversation(id) {
  return request({
    url: `/ai/tavern/conversations/${id}`,
    method: "get",
  });
}

export function updateConversation(id, data) {
  return request({
    url: `/ai/tavern/conversations/${id}`,
    method: "put",
    data,
  });
}

export function delConversation(id) {
  return request({
    url: `/ai/tavern/conversations/${id}`,
    method: "delete",
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
    headers: {
      repeatSubmit: false,
      interval: 500,
    },
  });
}

export function updateMessage(id, data) {
  return request({
    url: `/ai/tavern/messages/${id}`,
    method: "put",
    data,
  });
}

export function rebuildSummary(conversationId) {
  return request({
    url: `/ai/tavern/conversations/${conversationId}/summary/rebuild`,
    method: "post",
    timeout: 60000,
  });
}
