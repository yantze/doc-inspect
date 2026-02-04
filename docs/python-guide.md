# Python 入门指南

## 什么是 Python

Python 是一种高级、通用、解释型的编程语言。它由 Guido van Rossum 创建，于 1991 年首次发布。Python 的设计哲学强调代码的可读性和简洁性。

Python 支持多种编程范式，包括：
- 面向对象编程
- 函数式编程
- 过程式编程

## 安装 Python

### Windows 安装

1. 访问 Python 官网 https://python.org
2. 下载最新版本的 Windows 安装包
3. 运行安装程序，勾选 "Add Python to PATH"
4. 完成安装

### macOS 安装

macOS 通常预装了 Python，但建议使用 Homebrew 安装最新版本：

```bash
brew install python
```

### Linux 安装

大多数 Linux 发行版都预装了 Python，也可以使用包管理器安装：

```bash
# Ubuntu/Debian
sudo apt install python3

# CentOS/RHEL
sudo yum install python3
```

## 基础语法

### 变量和数据类型

Python 是动态类型语言，不需要声明变量类型：

```python
# 整数
age = 25

# 浮点数
price = 19.99

# 字符串
name = "Alice"

# 布尔值
is_active = True

# 列表
fruits = ["apple", "banana", "orange"]

# 字典
person = {"name": "Bob", "age": 30}
```

### 条件语句

```python
if age >= 18:
    print("成年人")
elif age >= 13:
    print("青少年")
else:
    print("儿童")
```

### 循环

```python
# for 循环
for fruit in fruits:
    print(fruit)

# while 循环
count = 0
while count < 5:
    print(count)
    count += 1
```

## 函数定义

```python
def greet(name, greeting="Hello"):
    """
    向指定的人问好
    
    Args:
        name: 人名
        greeting: 问候语，默认为 Hello
    
    Returns:
        问候字符串
    """
    return f"{greeting}, {name}!"

# 调用函数
message = greet("World")
print(message)  # 输出: Hello, World!
```

## 常用库

- **NumPy**: 科学计算和数组操作
- **Pandas**: 数据分析和处理
- **Matplotlib**: 数据可视化
- **Requests**: HTTP 请求
- **Flask/Django**: Web 开发框架
