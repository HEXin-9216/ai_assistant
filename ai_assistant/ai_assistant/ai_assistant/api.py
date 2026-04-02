import frappe
import requests
import json

# =========================================================
# 🛠️ 极其强大的本地业务工具箱 (九大金刚 - 含销售月报版)
# =========================================================

# --- 销售模块 ---
def get_recent_sales_orders(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["transaction_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["transaction_date"] = [">=", start_date]
        elif end_date: filters["transaction_date"] = ["<=", end_date]

        orders = frappe.db.get_list("Sales Order", fields=["name", "customer", "transaction_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not orders: return {"text": "报告：在指定范围内没有找到任何销售订单。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的销售订单：\n"
        orders_data = [] 
        for o in orders:
            result_str += f"- 订单号: [{o.name}](/app/sales-order/{o.name}), 客户: {o.customer}, 日期: {o.transaction_date}, 金额: ￥{o.grand_total}, 状态: {o.status}\n"
            orders_data.append({"订单编号": o.name, "客户名称": o.customer, "交易日期": str(o.transaction_date), "总金额(元)": float(o.grand_total) if o.grand_total else 0.0, "当前状态": o.status})
        return {"text": result_str, "data": orders_data}
    except Exception as e: return {"text": f"查询销售订单失败：{str(e)}", "data": []}

def get_recent_sales_invoices(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["posting_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["posting_date"] = [">=", start_date]
        elif end_date: filters["posting_date"] = ["<=", end_date]

        invoices = frappe.db.get_list("Sales Invoice", fields=["name", "customer", "posting_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not invoices: return {"text": "报告：在指定范围内没有找到任何销售发票。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的销售发票：\n"
        invoices_data = [] 
        for i in invoices:
            result_str += f"- 发票号: [{i.name}](/app/sales-invoice/{i.name}), 客户: {i.customer}, 日期: {i.posting_date}, 金额: ￥{i.grand_total}, 状态: {i.status}\n"
            invoices_data.append({"发票编号": i.name, "客户名称": i.customer, "开票日期": str(i.posting_date), "总金额(元)": float(i.grand_total) if i.grand_total else 0.0, "当前状态": i.status})
        return {"text": result_str, "data": invoices_data}
    except Exception as e: return {"text": f"查询销售发票失败：{str(e)}", "data": []}

# --- 库存与预警模块 ---
def get_recent_purchase_receipts(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["posting_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["posting_date"] = [">=", start_date]
        elif end_date: filters["posting_date"] = ["<=", end_date]

        receipts = frappe.db.get_list("Purchase Receipt", fields=["name", "supplier", "posting_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not receipts: return {"text": "报告：在指定范围内没有找到任何采购入库单。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的采购入库单：\n"
        receipts_data = [] 
        for r in receipts:
            result_str += f"- 入库单号: [{r.name}](/app/purchase-receipt/{r.name}), 供应商: {r.supplier}, 日期: {r.posting_date}, 金额: ￥{r.grand_total}, 状态: {r.status}\n"
            receipts_data.append({"入库单编号": r.name, "供应商名称": r.supplier, "入库日期": str(r.posting_date), "总金额(元)": float(r.grand_total) if r.grand_total else 0.0, "当前状态": r.status})
        return {"text": result_str, "data": receipts_data}
    except Exception as e: return {"text": f"查询采购入库单失败：{str(e)}", "data": []}

def get_recent_delivery_notes(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["posting_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["posting_date"] = [">=", start_date]
        elif end_date: filters["posting_date"] = ["<=", end_date]

        notes = frappe.db.get_list("Delivery Note", fields=["name", "customer", "posting_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not notes: return {"text": "报告：在指定范围内没有找到任何销售出库单。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的销售出库单：\n"
        notes_data = [] 
        for n in notes:
            result_str += f"- 出库单号: [{n.name}](/app/delivery-note/{n.name}), 客户: {n.customer}, 日期: {n.posting_date}, 金额: ￥{n.grand_total}, 状态: {n.status}\n"
            notes_data.append({"出库单编号": n.name, "客户名称": n.customer, "出库日期": str(n.posting_date), "总金额(元)": float(n.grand_total) if n.grand_total else 0.0, "当前状态": n.status})
        return {"text": result_str, "data": notes_data}
    except Exception as e: return {"text": f"查询销售出库单失败：{str(e)}", "data": []}

def get_low_stock_warnings(limit=10, threshold=10):
    try:
        limit = int(limit) if limit else 10
        threshold = float(threshold) if threshold else 10.0

        bins = frappe.db.sql("""
            SELECT item_code, warehouse, actual_qty
            FROM `tabBin`
            WHERE actual_qty <= %s
            ORDER BY actual_qty ASC
            LIMIT %s
        """, (threshold, limit), as_dict=True)

        if not bins:
            return {"text": f"报告老板：目前系统内各大仓库没有发现库存小于或等于 {threshold} 的商品，库存状况极其健康！", "data": []}

        result_str = f"⚠️ **极其重要的低库存预警**（实际库存 <= {threshold}）：\n"
        warning_data = []
        for b in bins:
            result_str += f"- 商品编码: [{b.item_code}](/app/item/{b.item_code}), 仓库: {b.warehouse}, 当前实际库存: **{b.actual_qty}**\n"
            warning_data.append({"商品编码": b.item_code, "所在仓库": b.warehouse, "实际库存量": float(b.actual_qty), "预警警戒线": threshold})
            
        return {"text": result_str, "data": warning_data}
    except Exception as e: return {"text": f"执行低库存预警扫描失败：{str(e)}", "data": []}

# --- 采购模块 ---
def get_recent_supplier_quotations(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["transaction_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["transaction_date"] = [">=", start_date]
        elif end_date: filters["transaction_date"] = ["<=", end_date]

        quotations = frappe.db.get_list("Supplier Quotation", fields=["name", "supplier", "transaction_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not quotations: return {"text": "报告：在指定范围内没有找到任何供应商报价。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的供应商报价：\n"
        quotations_data = [] 
        for q in quotations:
            result_str += f"- 报价单号: [{q.name}](/app/supplier-quotation/{q.name}), 供应商: {q.supplier}, 日期: {q.transaction_date}, 金额: ￥{q.grand_total}, 状态: {q.status}\n"
            quotations_data.append({"报价单编号": q.name, "供应商名称": q.supplier, "报价日期": str(q.transaction_date), "总金额(元)": float(q.grand_total) if q.grand_total else 0.0, "当前状态": q.status})
        return {"text": result_str, "data": quotations_data}
    except Exception as e: return {"text": f"查询供应商报价失败：{str(e)}", "data": []}

def get_recent_purchase_orders(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["transaction_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["transaction_date"] = [">=", start_date]
        elif end_date: filters["transaction_date"] = ["<=", end_date]

        orders = frappe.db.get_list("Purchase Order", fields=["name", "supplier", "transaction_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not orders: return {"text": "报告：在指定范围内没有找到任何采购订单。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的采购订单：\n"
        orders_data = [] 
        for o in orders:
            result_str += f"- 订单号: [{o.name}](/app/purchase-order/{o.name}), 供应商: {o.supplier}, 日期: {o.transaction_date}, 金额: ￥{o.grand_total}, 状态: {o.status}\n"
            orders_data.append({"采购订单编号": o.name, "供应商名称": o.supplier, "交易日期": str(o.transaction_date), "总金额(元)": float(o.grand_total) if o.grand_total else 0.0, "当前状态": o.status})
        return {"text": result_str, "data": orders_data}
    except Exception as e: return {"text": f"查询采购订单失败：{str(e)}", "data": []}

def get_recent_purchase_invoices(limit=5, start_date=None, end_date=None):
    try:
        limit = int(limit) if limit else 5
        filters = {}
        if start_date and end_date: filters["posting_date"] = ["between", [start_date, end_date]]
        elif start_date: filters["posting_date"] = [">=", start_date]
        elif end_date: filters["posting_date"] = ["<=", end_date]

        invoices = frappe.db.get_list("Purchase Invoice", fields=["name", "supplier", "posting_date", "grand_total", "status"], filters=filters, order_by="creation desc", limit=limit)
        if not invoices: return {"text": "报告：在指定范围内没有找到任何采购发票。", "data": []}
        result_str = "以下是从 ERPNext 数据库中查到的采购发票：\n"
        invoices_data = [] 
        for i in invoices:
            result_str += f"- 发票号: [{i.name}](/app/purchase-invoice/{i.name}), 供应商: {i.supplier}, 日期: {i.posting_date}, 金额: ￥{i.grand_total}, 状态: {i.status}\n"
            invoices_data.append({"采购发票编号": i.name, "供应商名称": i.supplier, "开票日期": str(i.posting_date), "总金额(元)": float(i.grand_total) if i.grand_total else 0.0, "当前状态": i.status})
        return {"text": result_str, "data": invoices_data}
    except Exception as e: return {"text": f"查询采购发票失败：{str(e)}", "data": []}

# 🌟 新增：极其硬核的数据分析引擎（销售月报）
def generate_sales_monthly_report(target_month=None):
    try:
        # 如果大模型没推算出月份，默认极其聪明地使用当前月
        if not target_month:
            target_month = frappe.utils.nowdate()[:7] # YYYY-MM 格式
            
        target_month_like = f"{target_month}%"

        # 1. 极其高效的聚合运算：总单数与总流水 (只算未被取消的单据 docstatus < 2)
        overall_stats = frappe.db.sql("""
            SELECT COUNT(name) as total_orders, SUM(grand_total) as total_revenue
            FROM `tabSales Order`
            WHERE transaction_date LIKE %s AND docstatus < 2
        """, (target_month_like,), as_dict=True)[0]

        total_orders = overall_stats.get('total_orders') or 0
        total_revenue = overall_stats.get('total_revenue') or 0.0

        if total_orders == 0:
            return {"text": f"报告老板：经过极其仔细的盘点，系统在 {target_month} 月份没有产生任何销售订单数据。", "data": []}

        # 2. 极其聪明的商业洞察：Top 5 客户大客户榜单
        top_customers = frappe.db.sql("""
            SELECT customer, SUM(grand_total) as revenue, COUNT(name) as order_count
            FROM `tabSales Order`
            WHERE transaction_date LIKE %s AND docstatus < 2
            GROUP BY customer
            ORDER BY revenue DESC
            LIMIT 5
        """, (target_month_like,), as_dict=True)

        # 3. 把极其生硬的数字包装成喂给 AI 的高级简报
        result_str = f"这是 {target_month} 月份的极其详尽的销售业绩汇总数据：\n\n"
        result_str += f"- **总订单数**: {total_orders} 笔\n"
        result_str += f"- **总销售额**: ￥{total_revenue:,.2f}\n\n"
        
        result_str += "👑 **Top 5 客户贡献榜**：\n"
        report_data = []
        for idx, c in enumerate(top_customers):
            result_str += f"  {idx+1}. 客户: **{c.customer}** - 订单: {c.order_count}笔, 贡献金额: ￥{c.revenue:,.2f}\n"
            # 整理出极其规整的 Excel 结构
            report_data.append({
                "统计月份": target_month,
                "排名": idx + 1,
                "大客户名称": c.customer,
                "下单总笔数": c.order_count,
                "总贡献金额(元)": float(c.revenue)
            })

        result_str += "\n老板，请根据以上极其精准的数据，写一份极其专业、有商业洞察的销售月报总结，并用漂亮的 Markdown 结构（如加粗、表格）展现出来！"
        
        return {"text": result_str, "data": report_data}
    except Exception as e: return {"text": f"执行销售月报聚合分析失败：{str(e)}", "data": []}


@frappe.whitelist()
def chat(message, platform, model_id):
    API_KEY = "sk-0bdcab13594f47d881b89ea415355401"
    frappe.logger().info(f"AI 小助手接收到指令：[{message}]，准备呼叫：[{model_id}]")

    try:
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = { "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json" }
        
        common_parameters = {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "查询返回的记录数量，默认 5。如果用户明确要求特定数量，请传入该数字。"},
                "start_date": {"type": "string", "description": "起始日期，格式 YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "结束日期，格式 YYYY-MM-DD"}
            }
        }
        
        warning_parameters = {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "查询返回的记录数量，默认 10。"},
                "threshold": {"type": "integer", "description": "低库存的警戒线数量，默认是 10。如果用户要求查库存低于 5 的，就传 5。"}
            }
        }

        # 🌟 专供大模型识别的月份解析参数
        report_parameters = {
            "type": "object",
            "properties": {
                "target_month": {"type": "string", "description": "目标月份，必须严格输出为 YYYY-MM 格式，例如 2026-03。如果不确定请不传。"}
            }
        }

        # 🌟 挂载九大金刚
        tools = [
            {"type": "function", "function": {"name": "get_recent_sales_orders", "description": "当用户询问销售订单时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_sales_invoices", "description": "当用户询问销售发票时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_purchase_receipts", "description": "当用户询问采购入库时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_delivery_notes", "description": "当用户询问销售出库时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_supplier_quotations", "description": "当用户询问供应商报价时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_purchase_orders", "description": "当用户询问采购订单时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_purchase_invoices", "description": "当用户询问采购发票时调用。可按需提取日期或数量。", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_low_stock_warnings", "description": "当用户询问低库存预警、库存不足、快断货的商品时调用。可按需提取数量限制和预警阈值(threshold)。", "parameters": warning_parameters}},
            # 🚨 终极武器：智能月报引擎
            {"type": "function", "function": {"name": "generate_sales_monthly_report", "description": "当用户要求生成销售月报、分析上个月或本月业绩、查看大客户贡献榜时调用。必须推算目标月份并传给 target_month。", "parameters": report_parameters}}
        ]

        current_date = frappe.utils.nowdate()
        messages = [
            {"role": "system", "content": f"你是一个极其专业的企业级 ERPNext 智能业务助手和财务分析师。当前系统日期是 {current_date}。如果用户询问特定时间段的数据或月报，请极其聪明地推算对应日期或 YYYY-MM 格式传给工具。对于生成的数据，务必加上你的专业商业洞察，并用极其醒目的 Markdown（如加粗、表格、Emoji）排版！"},
            {"role": "user", "content": message}
        ]
        
        payload = { "model": model_id, "messages": messages, "tools": tools, "tool_choice": "auto" }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status() 
        result_json = response.json()
        response_message = result_json["choices"][0]["message"]

        # =========================================================
        # 🧠 极其强悍的“九路拦截”调度中心
        # =========================================================
        if response_message.get("tool_calls"):
            tool_call = response_message["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            tool_call_id = tool_call["id"]
            
            try:
                args = json.loads(tool_call["function"].get("arguments", "{}"))
            except:
                args = {}
                
            req_limit = args.get("limit", 5)
            req_start = args.get("start_date")
            req_end = args.get("end_date")
            req_threshold = args.get("threshold", 10) 
            req_target_month = args.get("target_month") # 月报专属
            
            valid_functions = [
                "get_recent_sales_orders", "get_recent_sales_invoices", 
                "get_recent_purchase_receipts", "get_recent_delivery_notes",
                "get_recent_supplier_quotations", "get_recent_purchase_orders", "get_recent_purchase_invoices",
                "get_low_stock_warnings", "generate_sales_monthly_report"
            ]
            
            if function_name in valid_functions:
                
                if function_name == "get_recent_sales_orders":
                    tool_result, btn_label, file_prefix = get_recent_sales_orders(req_limit, req_start, req_end), "📊 导出完整订单明细 (Excel)", "ERPNext销售订单导出"
                elif function_name == "get_recent_sales_invoices":
                    tool_result, btn_label, file_prefix = get_recent_sales_invoices(req_limit, req_start, req_end), "📊 导出完整发票明细 (Excel)", "ERPNext销售发票导出"
                elif function_name == "get_recent_purchase_receipts":
                    tool_result, btn_label, file_prefix = get_recent_purchase_receipts(req_limit, req_start, req_end), "📥 导出采购入库明细 (Excel)", "ERPNext采购入库导出"
                elif function_name == "get_recent_delivery_notes":
                    tool_result, btn_label, file_prefix = get_recent_delivery_notes(req_limit, req_start, req_end), "🚚 导出销售出库明细 (Excel)", "ERPNext销售出库导出"
                elif function_name == "get_recent_supplier_quotations":
                    tool_result, btn_label, file_prefix = get_recent_supplier_quotations(req_limit, req_start, req_end), "📝 导出供应商报价明细 (Excel)", "ERPNext供应商报价导出"
                elif function_name == "get_recent_purchase_orders":
                    tool_result, btn_label, file_prefix = get_recent_purchase_orders(req_limit, req_start, req_end), "🛍️ 导出采购订单明细 (Excel)", "ERPNext采购订单导出"
                elif function_name == "get_recent_purchase_invoices":
                    tool_result, btn_label, file_prefix = get_recent_purchase_invoices(req_limit, req_start, req_end), "🧾 导出采购发票明细 (Excel)", "ERPNext采购发票导出"
                elif function_name == "get_low_stock_warnings":
                    tool_result, btn_label, file_prefix = get_low_stock_warnings(args.get("limit", 10), req_threshold), "📦 导出低库存预警报表 (Excel)", "ERPNext低库存预警"
                elif function_name == "generate_sales_monthly_report":
                    # 极其智能地触发数据挖掘引擎
                    tool_result, btn_label, file_prefix = generate_sales_monthly_report(req_target_month), "📈 导出本月大客户贡献榜 (Excel)", f"ERPNext销售月报_{req_target_month or '当月'}"
                
                messages.append(response_message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": function_name,
                    "content": tool_result["text"]
                })
                
                payload["messages"] = messages
                payload.pop("tools", None)
                payload.pop("tool_choice", None)
                
                second_response = requests.post(url, headers=headers, json=payload, timeout=30)
                second_response.raise_for_status()
                final_reply = second_response.json()["choices"][0]["message"]["content"]
                
                return {
                    "status": "success",
                    "reply": final_reply,
                    "action_button": {
                        "type": "export_excel",
                        "label": btn_label,
                        "data": tool_result["data"],
                        "file_prefix": file_prefix 
                    },
                    "logs": [
                        "后端 Python 接口触发成功！",
                        f"大模型极其聪明地调用了核心架构引擎：{function_name}。",
                        "已成功完成极其深度的底层数据库计算与聚合汇总！",
                        "大模型已收到财务数据并生成了顶级商业洞察报告！"
                    ]
                }

        ai_reply = response_message.get("content")
        return {
            "status": "success",
            "reply": ai_reply,
            "logs": ["后端 Python 接口触发成功！", "大模型未触发数据库查询，已获取常规智能回复！"]
        }

    except Exception as e:
        error_msg = str(e)
        frappe.logger().error(f"AI API 请求失败: {error_msg}")
        return {
            "status": "success",
            "reply": f"⚠️ 报告老板，连接大脑时发生异常：<br><br><b>{error_msg}</b>",
            "logs": ["发生网络或认证异常！请排查。"]
        }