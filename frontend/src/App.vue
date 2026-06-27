<script setup></script>

<template>
  <nav>
    <router-link to="/">聊天</router-link> |
    <router-link to="/docs">知识库</router-link> |
    <router-link to="/vectordb">向量库</router-link>
  </nav>
  <router-view />
</template>

<style>
nav {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

nav a {
  text-decoration: none;
  color: #409eff;
  font-size: 14px;
}

nav a.router-link-active {
  font-weight: bold;
  color: #337ecc;
}
</style>
