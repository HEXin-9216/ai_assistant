import frappe
import requests
import json

# =========================================================
# 🛠️ 极其强大的本地业务工具箱 (十二大金刚 - 含成本烧钱追踪)
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

# --- 财务及分析模块 ---
def generate_sales_monthly_report(target_month=None):
    try:
        if not target_month:
            target_month = frappe.utils.nowdate()[:7] 
            
        target_month_like = f"{target_month}%"

        overall_stats = frappe.db.sql("""
            SELECT COUNT(name) as total_orders, SUM(grand_total) as total_revenue
            FROM `tabSales Order`
            WHERE transaction_date LIKE %s AND docstatus < 2
        """, (target_month_like,), as_dict=True)[0]

        total_orders = overall_stats.get('total_orders') or 0
        total_revenue = overall_stats.get('total_revenue') or 0.0

        if total_orders == 0:
            return {"text": f"报告老板：经过极其仔细的盘点，系统在 {target_month} 月份没有产生任何销售订单数据。", "data": []}

        top_customers = frappe.db.sql("""
            SELECT customer, SUM(grand_total) as revenue, COUNT(name) as order_count
            FROM `tabSales Order`
            WHERE transaction_date LIKE %s AND docstatus < 2
            GROUP BY customer
            ORDER BY revenue DESC
            LIMIT 5
        """, (target_month_like,), as_dict=True)

        result_str = f"这是 {target_month} 月份的极其详尽的销售业绩汇总数据：\n\n"
        result_str += f"- **总订单数**: {total_orders} 笔\n"
        result_str += f"- **总销售额**: ￥{total_revenue:,.2f}\n\n"
        
        result_str += "👑 **Top 5 客户贡献榜**：\n"
        report_data = []
        for idx, c in enumerate(top_customers):
            result_str += f"  {idx+1}. 客户: **{c.customer}** - 订单: {c.order_count}笔, 贡献金额: ￥{c.revenue:,.2f}\n"
            report_data.append({
                "统计月份": target_month, "排名": idx + 1, "大客户名称": c.customer,
                "下单总笔数": c.order_count, "总贡献金额(元)": float(c.revenue)
            })

        result_str += "\n老板，请根据以上极其精准的数据，写一份极其专业、有商业洞察的销售月报总结，并用漂亮的 Markdown 结构（如加粗、表格）展现出来！"
        return {"text": result_str, "data": report_data}
    except Exception as e: return {"text": f"执行销售月报聚合分析失败：{str(e)}", "data": []}

def get_overdue_sales_invoices(limit=10):
    try:
        limit = int(limit) if limit else 10
        overdue_invoices = frappe.db.sql("""
            SELECT name, customer, posting_date, due_date, grand_total, outstanding_amount, DATEDIFF(CURDATE(), due_date) as overdue_days
            FROM `tabSales Invoice`
            WHERE docstatus = 1 AND outstanding_amount > 0 AND due_date < CURDATE()
            ORDER BY overdue_days DESC, outstanding_amount DESC
            LIMIT %s
        """, (limit,), as_dict=True)

        if not overdue_invoices:
            return {"text": "🎉 报告老板：系统内极其干净！没有任何逾期未收的销售账款，现金流极其健康！", "data": []}

        total_overdue = sum([float(i.outstanding_amount) for i in overdue_invoices])

        result_str = f"🚨 **极其紧急的催款雷达警告！**\n"
        result_str += f"以下是当前系统内拖欠时间最长的账款单据（前 {limit} 笔），请务必尽快安排财务催收：\n\n"
        
        report_data = []
        for i in overdue_invoices:
            result_str += f"- 客户: **{i.customer}** | 发票: [{i.name}](/app/sales-invoice/{i.name}) | 逾期天数: **{i.overdue_days}天** | 未收金额: **￥{i.outstanding_amount:,.2f}**\n"
            report_data.append({
                "发票编号": i.name, "大客户名称": i.customer, "开票日期": str(i.posting_date),
                "最晚收款日": str(i.due_date), "发票总金额(元)": float(i.grand_total),
                "拖欠未付金额(元)": float(i.outstanding_amount), "已逾期天数": int(i.overdue_days)
            })

        result_str += f"\n💰 **总计预警待收金额**: **￥{total_overdue:,.2f}**\n"
        result_str += "\n老板，我已经为您整理了极度详细的 Excel 催款清单，请直接点击下方按钮导出，以便发送给销售或财务部门进行精准催收！"
        
        return {"text": result_str, "data": report_data}
    except Exception as e: return {"text": f"执行智能催款雷达扫描失败：{str(e)}", "data": []}

def get_financial_health_summary():
    try:
        gl_summary = frappe.db.sql("""
            SELECT a.root_type, SUM(gle.debit) as total_debit, SUM(gle.credit) as total_credit
            FROM `tabGL Entry` gle
            JOIN `tabAccount` a ON gle.account = a.name
            WHERE gle.is_cancelled = 0
            GROUP BY a.root_type
        """, as_dict=True)

        assets, liabilities, income, expense = 0.0, 0.0, 0.0, 0.0

        for row in gl_summary:
            if row.root_type == 'Asset':
                assets += float(row.total_debit or 0) - float(row.total_credit or 0)
            elif row.root_type == 'Liability':
                liabilities += float(row.total_credit or 0) - float(row.total_debit or 0)
            elif row.root_type == 'Income':
                income += float(row.total_credit or 0) - float(row.total_debit or 0)
            elif row.root_type == 'Expense':
                expense += float(row.total_debit or 0) - float(row.total_credit or 0)

        net_profit = income - expense

        result_str = "🏥 **企业极其核心的财务体检简报**：\n\n"
        result_str += f"- **总资产 (Assets)**: ￥{assets:,.2f}\n"
        result_str += f"- **总负债 (Liabilities)**: ￥{liabilities:,.2f}\n"
        result_str += f"- **累计收入 (Income)**: ￥{income:,.2f}\n"
        result_str += f"- **累计支出 (Expense)**: ￥{expense:,.2f}\n"
        result_str += f"- **当前账面净利润 (Net Profit)**: **￥{net_profit:,.2f}**\n\n"

        if net_profit < 0:
            result_str += "⚠️ **极其严肃的洞察警报**：老板，咱们目前的账面净利润处于**亏损状态**！请密切关注现金流储备，并核查近期大额支出科目！\n"
        elif net_profit > 0 and assets > liabilities:
            result_str += "✅ **极其振奋的洞察报告**：老板，公司目前的资产负债极其健康，账面实现**盈利**！请继续保持极其凶猛的增长势头！\n"
        else:
            result_str += "💡 **架构师洞察**：老板，目前利润为正，但请同步关注资产负债率，确保资金链极其充沛。\n"

        report_data = [{
            "体检日期": str(frappe.utils.today()),
            "总资产(元)": assets, "总负债(元)": liabilities,
            "总计收入(元)": income, "总计支出(元)": expense, "净利润(元)": net_profit
        }]

        return {"text": result_str, "data": report_data}
    except Exception as e: return {"text": f"执行财务体检失败：{str(e)}", "data": []}

# 🌟 极其炸裂的新增核武：成本中心“烧钱”追踪器
def get_cost_center_expenses(cost_center=None, target_month=None, limit=10):
    try:
        limit = int(limit) if limit else 10
        
        conditions = ["a.root_type = 'Expense'", "gle.is_cancelled = 0"]
        values = []

        if target_month:
            conditions.append("gle.posting_date LIKE %s")
            values.append(f"{target_month}%")
        
        if cost_center:
            conditions.append("gle.cost_center LIKE %s")
            values.append(f"%{cost_center}%")

        where_clause = " AND ".join(conditions)

        # 极其霸气地跨表求和计算净花销
        query = f"""
            SELECT gle.account, gle.cost_center, SUM(gle.debit - gle.credit) as net_expense
            FROM `tabGL Entry` gle
            JOIN `tabAccount` a ON gle.account = a.name
            WHERE {where_clause}
            GROUP BY gle.account, gle.cost_center
            HAVING net_expense > 0
            ORDER BY net_expense DESC
            LIMIT %s
        """
        values.append(limit)

        expenses = frappe.db.sql(query, tuple(values), as_dict=True)

        if not expenses:
            return {"text": f"🎉 报告老板：在指定条件（月份：{target_month or '全部'}，成本中心：{cost_center or '全部'}）下没有发现任何支出记录！", "data": []}

        total_expense = sum([float(e.net_expense) for e in expenses])

        result_str = f"💸 **极其清晰的成本“烧钱”追踪明细**（月份：{target_month or '全部'} | 成本中心：{cost_center or '全部'}）：\n\n"
        
        report_data = []
        for e in expenses:
            result_str += f"- 科目: **{e.account}** | 成本中心: {e.cost_center} | 净支出: **￥{e.net_expense:,.2f}**\n"
            report_data.append({
                "统计月份": target_month or "全部",
                "成本中心": e.cost_center or "未指定",
                "支出科目": e.account,
                "净支出金额(元)": float(e.net_expense)
            })

        result_str += f"\n🔥 **总计排查出上述科目的总支出**: **￥{total_expense:,.2f}**\n"
        result_str += "\n老板，我已经为您揪出了极其具体的花销科目！请结合上述数据，为各部门下达极其严格的成本管控指令！"
        
        return {"text": result_str, "data": report_data}
    except Exception as e: return {"text": f"执行成本追踪扫描失败：{str(e)}", "data": []}


@frappe.whitelist()
def chat(message, platform, model_id):
    API_KEY = "sk-0bdcab13594f47d881b89ea415355401"
    frappe.logger().info(f"AI 小助手接收到指令：[{message}]，准备呼叫：[{model_id}]")

    try:
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = { "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json" }
        
        common_parameters = { "type": "object", "properties": { "limit": {"type": "integer", "description": "返回数量限制"}, "start_date": {"type": "string"}, "end_date": {"type": "string"} } }
        warning_parameters = { "type": "object", "properties": { "limit": {"type": "integer"}, "threshold": {"type": "integer"} } }
        report_parameters = { "type": "object", "properties": { "target_month": {"type": "string", "description": "YYYY-MM"} } }
        overdue_parameters = { "type": "object", "properties": { "limit": {"type": "integer"} } }
        expense_parameters = { "type": "object", "properties": { "target_month": {"type": "string", "description": "YYYY-MM"}, "cost_center": {"type": "string", "description": "成本中心名称，例如 'jd-test'"}, "limit": {"type": "integer"} } }

        # 🌟 挂载全套十二大金刚
        tools = [
            {"type": "function", "function": {"name": "get_recent_sales_orders", "description": "当用户询问销售订单时调用", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_sales_invoices", "description": "当用户询问销售发票时调用", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_purchase_receipts", "description": "当用户询问采购入库时调用", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_delivery_notes", "description": "当用户询问销售出库时调用", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_supplier_quotations", "description": "当用户询问供应商报价时调用", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_purchase_orders", "description": "当用户询问采购订单时调用", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_recent_purchase_invoices", "description": "当用户询问采购发票时调用", "parameters": common_parameters}},
            {"type": "function", "function": {"name": "get_low_stock_warnings", "description": "当用户询问低库存预警时调用", "parameters": warning_parameters}},
            {"type": "function", "function": {"name": "generate_sales_monthly_report", "description": "当用户要求生成销售月报时调用", "parameters": report_parameters}},
            {"type": "function", "function": {"name": "get_overdue_sales_invoices", "description": "当用户要求查询逾期账款或催款清单时调用", "parameters": overdue_parameters}},
            {"type": "function", "function": {"name": "get_financial_health_summary", "description": "当用户要求查询财务体检、公司总资产、总负债、利润、亏损、财务基本盘时调用。不需要任何参数。", "parameters": {"type": "object", "properties": {}}}},
            # 🚨 终极武器十二：成本中心烧钱追踪器
            {"type": "function", "function": {"name": "get_cost_center_expenses", "description": "当用户要求查询某个成本中心的花销、支出、烧钱情况或各项开销明细时调用", "parameters": expense_parameters}}
        ]

        # 🌟 极其严厉的防脑补紧箍咒版本！
        current_date = frappe.utils.nowdate()
        messages = [
            {"role": "system", "content": f"你是一个极其专业的企业级 ERPNext 智能业务助手和财务总监。当前日期是 {current_date}。请根据数据生成极其醒目专业的 Markdown 汇报（加粗、表格、Emoji）。\n\n🚨【极其严格的红线指令】：\n1. 绝对、严禁、不允许捏造、虚构、模拟任何数据库中没有返回的商品名称、客户名、成本中心、明细科目或金额！\n2. 数据库返回什么，你就只能输出什么。如果返回的数据极其粗糙、缺少名称或只有一条记录，请原样呈现，坦诚告知老板当前数据不完善，绝对不允许为了报表好看而自行脑补或填充假数据！"},
            {"role": "user", "content": message}
        ]
        
        payload = { "model": model_id, "messages": messages, "tools": tools, "tool_choice": "auto" }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status() 
        result_json = response.json()
        response_message = result_json["choices"][0]["message"]

        # =========================================================
        # 🧠 极其强悍的“十二路拦截”调度中心
        # =========================================================
        if response_message.get("tool_calls"):
            tool_call = response_message["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            tool_call_id = tool_call["id"]
            
            try: args = json.loads(tool_call["function"].get("arguments", "{}"))
            except: args = {}
            
            valid_functions = [
                "get_recent_sales_orders", "get_recent_sales_invoices", "get_recent_purchase_receipts", "get_recent_delivery_notes",
                "get_recent_supplier_quotations", "get_recent_purchase_orders", "get_recent_purchase_invoices",
                "get_low_stock_warnings", "generate_sales_monthly_report", "get_overdue_sales_invoices", "get_financial_health_summary",
                "get_cost_center_expenses"
            ]
            
            if function_name in valid_functions:
                if function_name == "get_recent_sales_orders": tool_result, btn_label, file_prefix = get_recent_sales_orders(args.get("limit", 5), args.get("start_date"), args.get("end_date")), "📊 导出订单", "ERPNext销售订单"
                elif function_name == "get_recent_sales_invoices": tool_result, btn_label, file_prefix = get_recent_sales_invoices(args.get("limit", 5), args.get("start_date"), args.get("end_date")), "📊 导出发票", "ERPNext销售发票"
                elif function_name == "get_recent_purchase_receipts": tool_result, btn_label, file_prefix = get_recent_purchase_receipts(args.get("limit", 5), args.get("start_date"), args.get("end_date")), "📥 导出入库", "ERPNext采购入库"
                elif function_name == "get_recent_delivery_notes": tool_result, btn_label, file_prefix = get_recent_delivery_notes(args.get("limit", 5), args.get("start_date"), args.get("end_date")), "🚚 导出出库", "ERPNext销售出库"
                elif function_name == "get_recent_supplier_quotations": tool_result, btn_label, file_prefix = get_recent_supplier_quotations(args.get("limit", 5), args.get("start_date"), args.get("end_date")), "📝 导出报价", "ERPNext供应商报价"
                elif function_name == "get_recent_purchase_orders": tool_result, btn_label, file_prefix = get_recent_purchase_orders(args.get("limit", 5), args.get("start_date"), args.get("end_date")), "🛍️ 导出订单", "ERPNext采购订单"
                elif function_name == "get_recent_purchase_invoices": tool_result, btn_label, file_prefix = get_recent_purchase_invoices(args.get("limit", 5), args.get("start_date"), args.get("end_date")), "🧾 导出发票", "ERPNext采购发票"
                elif function_name == "get_low_stock_warnings": tool_result, btn_label, file_prefix = get_low_stock_warnings(args.get("limit", 10), args.get("threshold", 10)), "📦 导出低库存预警", "ERPNext低库存"
                elif function_name == "generate_sales_monthly_report": tool_result, btn_label, file_prefix = generate_sales_monthly_report(args.get("target_month")), "📈 导出大客户榜", f"ERPNext销售月报"
                elif function_name == "get_overdue_sales_invoices": tool_result, btn_label, file_prefix = get_overdue_sales_invoices(args.get("limit", 10)), "💰 导出催款清单", "ERPNext催款清单"
                elif function_name == "get_financial_health_summary": tool_result, btn_label, file_prefix = get_financial_health_summary(), "🏥 导出财务体检报告 (Excel)", "ERPNext财务体检"
                # 🚨 触发成本烧钱追踪大招
                elif function_name == "get_cost_center_expenses": tool_result, btn_label, file_prefix = get_cost_center_expenses(args.get("cost_center"), args.get("target_month"), args.get("limit", 10)), "💸 导出成本追踪明细 (Excel)", "ERPNext成本追踪"

                messages.append(response_message)
                messages.append({"role": "tool", "tool_call_id": tool_call_id, "name": function_name, "content": tool_result["text"]})
                
                payload["messages"] = messages
                payload.pop("tools", None)
                payload.pop("tool_choice", None)
                
                second_response = requests.post(url, headers=headers, json=payload, timeout=30)
                second_response.raise_for_status()
                final_reply = second_response.json()["choices"][0]["message"]["content"]
                
                return {
                    "status": "success",
                    "reply": final_reply,
                    "action_button": { "type": "export_excel", "label": btn_label, "data": tool_result["data"], "file_prefix": file_prefix },
                    "logs": ["后端 Python 接口触发成功！", f"大模型极其聪明地调用了：{function_name}。"]
                }

        return {"status": "success", "reply": response_message.get("content"), "logs": ["大模型未触发数据库查询，已获取常规智能回复！"]}
    except Exception as e: return {"status": "success", "reply": f"⚠️ 连接大脑时发生异常：<br><br><b>{str(e)}</b>", "logs": ["发生异常！"]}