# 学习图谱生成器的 vis.js Network 格式参考

## 概述

本文档定义了与 **vis.js Network 库**兼容的学习图谱**标准 JSON 格式**。生成学习图谱时请使用此格式，以确保可视化正常工作。

## 目的

使用**学习图谱生成器技能**时，最终 JSON 输出必须符合本规范，才能与教育类 Web 应用中常用的 vis.js 网络可视化配合工作。

## JSON 结构

### 顶层 Schema

```json
{
  "nodes": [...],
  "edges": [...],
  "metadata": {...}
}
```

### 完整示例

```json
{
  "nodes": [
    {
      "id": 1,
      "label": "Complex Numbers",
      "group": "MATH"
    },
    {
      "id": 2,
      "label": "Euler's Formula",
      "group": "MATH"
    }
  ],
  "edges": [
    {
      "from": 1,
      "to": 2
    }
  ],
  "metadata": {
    "title": "Course Learning Graph",
    "description": "300-600 interconnected concepts",
    "nodeCount": 450,
    "edgeCount": 572,
    "taxonomies": {
      "MATH": "Mathematical Foundations",
      "FFT": "FFT Algorithm & Implementation"
    }
  }
}
```

## 节点格式

### 必需属性

| 属性 | 类型   | 说明                          | 示例               |
|----------|--------|--------------------------------------|-----------------------|
| `id`     | number | 唯一标识符（从 1 开始的索引）    | `1`、`2`、`3`        |
| `label`  | string | 显示文本（最多 32 字符）          | `"Complex Numbers"`  |

### 可选属性

| 属性 | 类型   | 说明                          | 示例               |
|----------|--------|--------------------------------------|-----------------------|
| `group`  | string | 用于样式着色的分类法/类别        | `"MATH"`、`"FFT"`    |
| `title`  | string | 悬停时的提示文本                | `"Foundational concept"` |
| `shape`  | string | 节点形状                           | `"dot"`、`"box"`、`"star"` |
| `color`  | string | 覆盖组颜色                 | `"red"`、`"#FF0000"` |
| `x`      | number | 固定的水平位置            | `-900`、`900`        |
| `y`      | number | 固定的垂直位置              | `0`、`100`           |
| `fixed`  | object | 锁定位置                        | `{"x": true, "y": false}` |

### 包含全部属性的节点示例

```json
{
  "id": 1,
  "label": "Complex Numbers",
  "group": "MATH",
  "title": "Foundational mathematical concept",
  "shape": "box",
  "color": "red",
  "x": -900,
  "fixed": {"x": true, "y": false}
}
```

## 边格式

### 必需属性

| 属性 | 类型   | 说明                          | 示例               |
|----------|--------|--------------------------------------|-----------------------|
| `from`   | number | 源节点 ID（先修概念）        | `1`                  |
| `to`     | number | 目标节点 ID（依赖者）           | `2`                  |

### 可选属性

| 属性 | 类型   | 说明                          | 示例               |
|----------|--------|--------------------------------------|-----------------------|
| `arrows` | string/object | 箭头方向                | `"to"`、`{"to": true}` |
| `color`  | string | 边颜色                           | `"gray"`、`"#888888"` |
| `width`  | number | 边粗细                       | `1`、`2`、`3`        |
| `label`  | string | 边上的文字                         | `"prerequisite"`     |
| `dashes` | boolean/array | 虚线样式               | `true`、`[5, 5]`     |

### 边示例

```json
{
  "from": 1,
  "to": 2,
  "arrows": "to",
  "color": "gray",
  "width": 1
}
```

## 元数据格式

可选，但建议用于文档化与分析。

### 标准元数据属性

```json
{
  "metadata": {
    "title": "FFT Benchmarking Course Learning Graph",
    "description": "300-600 interconnected concepts for a 10-week course",
    "nodeCount": 450,
    "edgeCount": 572,
    "version": "1.0",
    "generated": "2025-10-30",
    "taxonomies": {
      "MATH": "Mathematical Foundations",
      "FFT": "FFT Algorithm & Implementation",
      "SIG": "Signal Processing",
      "ARM": "ARM Architecture & DSP Hardware",
      "MEM": "Memory Management & Optimization",
      "FXP": "Fixed-Point Arithmetic",
      "BENCH": "Benchmarking & Testing",
      "LIB": "FFT Libraries & Integration",
      "OPT": "Optimization Techniques"
    }
  }
}
```

## 重要区分

### ❌ 错误：D3.js 格式

```json
{
  "nodes": [
    {
      "id": 1,
      "label": "Complex Numbers",
      "taxonomy": "MATH"          // ❌ Wrong property name
    }
  ],
  "links": [                      // ❌ Wrong array name
    {
      "source": 1,                // ❌ Wrong property name
      "target": 2                 // ❌ Wrong property name
    }
  ]
}
```

### ✅ 正确：vis.js 格式

```json
{
  "nodes": [
    {
      "id": 1,
      "label": "Complex Numbers",
      "group": "MATH"             // ✅ Correct for vis.js
    }
  ],
  "edges": [                      // ✅ Correct array name
    {
      "from": 1,                  // ✅ Correct property name
      "to": 2                     // ✅ Correct property name
    }
  ]
}
```

## Python 转换模板

### 标准 CSV 转 vis.js JSON 转换器

```python
#!/usr/bin/env python3
"""
Convert concept dependencies CSV to vis.js network JSON format.
"""

import csv
import json

def convert_csv_to_json(csv_file, json_file):
    """Convert CSV to vis.js network format."""
    nodes = []
    edges = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            concept_id = int(row['ConceptID'])
            label = row['ConceptLabel']
            taxonomy = row['TaxonomyID']
            deps = row['Dependencies'].strip()

            # Create node (vis.js format)
            node = {
                "id": concept_id,
                "label": label,
                "group": taxonomy
            }
            nodes.append(node)

            # Create edges (vis.js format: from/to)
            if deps:
                dependencies = [int(d) for d in deps.split('|')]
                for dep in dependencies:
                    edge = {
                        "from": dep,
                        "to": concept_id
                    }
                    edges.append(edge)

    # Create graph structure
    graph = {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "title": "Learning Graph",
            "nodeCount": len(nodes),
            "edgeCount": len(edges)
        }
    }

    # Write to JSON file
    with open(json_file, 'w') as f:
        json.dump(graph, f, indent=2)

    return graph
```

## JavaScript 加载模板

### 标准 vis.js Network 初始化

```javascript
function drawGraph() {
  // Fetch the graph data from JSON file
  fetch('learning-graph.json')
    .then(response => response.json())
    .then(data => {
      // Create DataSets for vis.js
      const nodes = new vis.DataSet(data.nodes);
      const edges = new vis.DataSet(data.edges);

      // Optional: Customize nodes after loading
      nodes.forEach(function (node) {
        if (node.group === "MATH") {
          node.x = -900;
          node.fixed = { x: true, y: false };
          node.shape = "box";
          node.color = "red";
        } else if (node.group === "OPT") {
          node.x = 900;
          node.fixed = { x: true, y: false };
          node.shape = "star";
          node.color = "gold";
        }
      });

      // Create network
      const container = document.getElementById('mynetwork');
      const graphData = {
        nodes: nodes,
        edges: edges
      };

      // Network options
      const options = {
        physics: {
          enabled: true,
          solver: 'forceAtlas2Based',
          stabilization: {
            iterations: 1000,
            updateInterval: 25
          }
        },
        edges: {
          arrows: {
            to: {
              enabled: true,
              type: 'arrow'
            }
          },
          smooth: {
            type: 'continuous'
          }
        },
        nodes: {
          shape: 'dot',
          size: 20,
          font: {
            size: 14,
            color: 'black'
          },
          borderWidth: 2
        }
      };

      // Initialize network
      const network = new vis.Network(container, graphData, options);
    })
    .catch(error => {
      console.error("Error loading JSON:", error);
    });
}
```

## 组/分类法颜色

教育分类法分组的推荐配色方案：

```javascript
const taxonomyColors = {
  "MATH": "#E74C3C",    // Red - Foundational
  "FFT": "#3498DB",     // Blue - Core algorithms
  "SIG": "#2ECC71",     // Green - Signal processing
  "ARM": "#9B59B6",     // Purple - Hardware
  "MEM": "#F39C12",     // Orange - Memory
  "FXP": "#1ABC9C",     // Teal - Numeric precision
  "BENCH": "#E67E22",   // Dark orange - Testing
  "LIB": "#95A5A6",     // Gray - Libraries
  "OPT": "#F1C40F"      // Yellow/Gold - Optimization
};
```

## 校验清单

为 vis.js 生成学习图谱 JSON 时，请核实：

- [ ] 顶层对象有 `nodes` 数组（不是 `vertices`）
- [ ] 顶层对象有 `edges` 数组（不是 `links`）
- [ ] 每个节点有 `id`（number）和 `label`（string）
- [ ] 节点使用 `group` 属性（不是 `taxonomy` 或 `category`）
- [ ] 每条边有 `from`（number）和 `to`（number）
- [ ] 边使用 `from`/`to`（不是 `source`/`target`）
- [ ] 所有 `from` 和 `to` 值都引用有效的节点 ID
- [ ] 没有自环（`from === to` 的边）
- [ ] 对学习路径而言图构成有效的 DAG（无环）
- [ ] 可选：包含 metadata 对象用于文档化

## 应避免的常见错误

| 错误 | 后果 | 解决方案 |
|---------|-------|----------|
| 使用 `links` | vis.js 找不到边 | 使用 `edges` |
| 使用 `source`/`target` | 边无法连接 | 使用 `from`/`to` |
| 使用 `taxonomy` | 分组不生效 | 使用 `group` |
| 字符串 ID | 类型不匹配错误 | 使用数值 ID |
| 缺少 `label` | 节点空白 | 始终包含标签 |
| 环形边 | 学习路径出现环 | 校验 DAG 结构 |

## 文件命名约定

**推荐：**
- `learning-graph.json`——主图文件
- `concept-dependencies.csv`——源 CSV 文件
- `convert-to-json.py`——转换脚本

**不推荐：**
- `graph.json`——过于笼统
- `network.json`——有歧义
- `data.json`——没有描述性

## vis.js 文档参考

- **官方文档：** https://visjs.github.io/vis-network/docs/network/
- **节点选项：** https://visjs.github.io/vis-network/docs/network/nodes.html
- **边选项：** https://visjs.github.io/vis-network/docs/network/edges.html
- **物理引擎：** https://visjs.github.io/vis-network/docs/network/physics.html
- **示例：** https://visjs.github.io/vis-network/examples/

## 技能生成要点总结

### 速查卡

**面向学习图谱生成器技能：**

1. **数组名：** `nodes` 和 `edges`（不是 links/vertices）
2. **节点结构：** `{id: number, label: string, group: string}`
3. **边结构：** `{from: number, to: number}`
4. **group 属性：** 用于分类法类别（启用着色）
5. **元数据：** 可选，但建议用于文档化
6. **校验：** 确保 DAG 结构（无环）
7. **Python 模板：** 使用所提供的转换器代码
8. **测试：** 在 vis.js Network 中加载以验证渲染

### 集成工作流

```
CSV (concept-dependencies.csv)
    ↓
Python Script (convert-to-json.py)
    ↓
JSON (learning-graph.json) [vis.js format]
    ↓
HTML + JavaScript (vis.Network)
    ↓
Interactive Graph Visualization
```

---

**文档版本：** 1.0
**创建日期：** 2025-10-30
**配套使用：** 学习图谱生成器技能
**目标库：** vis.js Network v9.x+
**状态：** 可用于生产环境的参考文档
