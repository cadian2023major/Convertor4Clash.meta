# Convertor4Clash.meta
Convertor for Clash.meta

## 用途
想找个订阅转换给Okgg用，发现主流的几乎都不支持clash.meta,自己写了一个，主要用处是把Vless节点的订阅抓换成Clash.meta支持的本地文件 （目前仅支持vless + grpc 和 vless + h2）

## clash.mate模板
[模板文件](https://gist.githubusercontent.com/cadian2023major/92f23933fb910b91cc81be44eed5d4fe/raw/a722421099d4e713549fad6e5b810154e5ddddc6/OriginRule.yaml)

## 规则组
ACL4SSR

## 使用说明
1.本项目目前仅支持 vless + grpc 和 vless + h2 格式 的订阅。
2.下载文件或者复制代码后，在代码中的订阅地址填写自己的订阅，本地完成转换，绝对安全。
3.除了原版以外还有一个特殊版，特殊版是为了使用链式代理中继访问能够支持chatgpt的节点而存在的，需要支持的条件比较多 。
  1) 拥有能够顺利访问的境外节点（该节点可能因为宽带属性不能访问chatgpt）
  2) 使用该节点中继到支持chatgpt的vless + grpc 或者 vless + h2节点。
相比于普通版的使用，除了订阅，还有一个位置是用来填写自己的节点信息的。需要注意的是，该转换会抛弃所有不支持chatgpt的节点。

## 更新日志
2023.5 添加链式代理(relay)转换.
