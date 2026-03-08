import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class UIManager:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.create_widgets()
    
    def on_tag_filter_change(self, event):
        """标签筛选变化事件处理"""
        tag_filter = self.tag_filter_var.get()
        if tag_filter == "自定义筛选":
            # 显示自定义筛选输入框
            self.custom_tag_label.grid()
            self.custom_tag_entry.grid()
        else:
            # 隐藏自定义筛选输入框
            self.custom_tag_label.grid_remove()
            self.custom_tag_entry.grid_remove()
    
    def create_widgets(self):
        # 创建主框架，左侧配置，右侧预览
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左侧配置区域
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill="y", padx=(0, 10))
        
        # 右侧预览区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill="both", expand=True)
        
        # AI配置
        config_frame = ttk.LabelFrame(left_frame, text="AI配置")
        config_frame.pack(fill="x", pady=(0, 10))
        
        # API Key
        ttk.Label(config_frame, text="API Key:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.api_key_var = tk.StringVar(value=self.app.config.get_api_key())
        ttk.Entry(config_frame, textvariable=self.api_key_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="we")
        self.api_key_var.trace_add("write", self.app.on_api_key_change)
        
        # API服务选择
        ttk.Label(config_frame, text="API服务:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.api_service_var = tk.StringVar(value="硅基流动")
        self.api_service_combobox = ttk.Combobox(config_frame, textvariable=self.api_service_var, width=15)
        self.api_service_combobox['values'] = list(self.app.api_options.keys()) + ["自定义"]
        self.api_service_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.api_service_combobox.bind("<<ComboboxSelected>>", self.app.on_api_service_change)
        
        # API Base
        ttk.Label(config_frame, text="API Base:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.api_base_var = tk.StringVar(value=self.app.config.get_api_base())
        ttk.Entry(config_frame, textvariable=self.api_base_var, width=30).grid(row=2, column=1, padx=5, pady=5, sticky="we")
        self.api_base_var.trace_add("write", self.app.on_api_base_change)
        
        # 模型选择
        ttk.Label(config_frame, text="模型:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.model_var = tk.StringVar(value=self.app.config.get_model())
        self.model_combobox = ttk.Combobox(config_frame, textvariable=self.model_var, width=27)
        self.model_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="we")
        self.model_var.trace_add("write", self.app.on_model_change)
        
        # 模型搜索
        ttk.Label(config_frame, text="搜索:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.model_search_var = tk.StringVar()
        self.model_search_entry = ttk.Entry(config_frame, textvariable=self.model_search_var, width=20)
        self.model_search_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.model_search_var.trace_add("write", self.app.on_model_search)
        
        # 搜索按钮
        ttk.Button(config_frame, text="过滤", command=self.app.on_model_search_button).grid(row=4, column=1, padx=5, pady=5, sticky="e")
        
        # 获取模型列表按钮
        ttk.Button(config_frame, text="获取模型列表", command=self.app.fetch_models).grid(row=3, column=2, padx=5, pady=5)
        
        # 牌组选择区域
        deck_frame = ttk.LabelFrame(left_frame, text="牌组选择")
        deck_frame.pack(fill="x", pady=(0, 10))
        
        # 牌组下拉框
        ttk.Label(deck_frame, text="选择牌组:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.deck_var = tk.StringVar(value="所有牌组")
        self.deck_combobox = ttk.Combobox(deck_frame, textvariable=self.deck_var, width=27)
        self.deck_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        
        # 获取牌组列表按钮
        ttk.Button(deck_frame, text="获取牌组列表", command=self.app.fetch_decks).grid(row=0, column=2, padx=5, pady=5)
        
        # 卡片数量
        ttk.Label(deck_frame, text="卡片数量:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.card_count_var = tk.StringVar(value="全部")
        self.card_count_combobox = ttk.Combobox(deck_frame, textvariable=self.card_count_var, width=8)
        self.card_count_combobox['values'] = ["5", "10", "20", "50", "全部"]
        self.card_count_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 标签筛选
        ttk.Label(deck_frame, text="标签筛选:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.tag_filter_var = tk.StringVar(value="有标签的卡片")
        self.tag_filter_combobox = ttk.Combobox(deck_frame, textvariable=self.tag_filter_var, width=15)
        self.tag_filter_combobox['values'] = ["全部卡片", "有标签的卡片", "无标签的卡片", "自定义筛选"]
        self.tag_filter_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # 自定义标签筛选输入框
        self.custom_tag_label = ttk.Label(deck_frame, text="标签字符筛选:")
        self.custom_tag_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.custom_tag_var = tk.StringVar(value="")
        self.custom_tag_entry = ttk.Entry(deck_frame, textvariable=self.custom_tag_var, width=15)
        self.custom_tag_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # 初始隐藏自定义筛选输入框
        self.custom_tag_label.grid_remove()
        self.custom_tag_entry.grid_remove()
        
        # 添加标签筛选变化事件
        self.tag_filter_combobox.bind("<<ComboboxSelected>>", self.on_tag_filter_change)
        
        # 自定义Prompt区域
        prompt_frame = ttk.LabelFrame(left_frame, text="自定义Prompt")
        prompt_frame.pack(fill="x", pady=(0, 10))
        
        # Prompt选择下拉框
        ttk.Label(prompt_frame, text="选择Prompt:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.prompt_name_var = tk.StringVar()
        self.prompt_combobox = ttk.Combobox(prompt_frame, textvariable=self.prompt_name_var, width=20)
        self.prompt_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.prompt_combobox.bind("<<ComboboxSelected>>", self.app.on_prompt_change)
        
        # 刷新Prompt按钮
        ttk.Button(prompt_frame, text="刷新", command=self.app.refresh_prompts).grid(row=0, column=2, padx=5, pady=5)
        
        # Prompt输入框
        ttk.Label(prompt_frame, text="提示语:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, width=35, height=4, wrap=tk.WORD)
        self.prompt_text.grid(row=1, column=1, padx=5, pady=5, sticky="we", columnspan=2)
        self.prompt_text.insert(tk.END, self.app.config.get_default_prompt())
        
        # 保存Prompt按钮
        ttk.Button(prompt_frame, text="保存当前Prompt", command=self.app.save_current_prompt).grid(row=2, column=1, padx=5, pady=5, sticky="e")
        
        # 删除Prompt按钮
        ttk.Button(prompt_frame, text="删除当前Prompt", command=self.app.delete_current_prompt).grid(row=3, column=1, padx=5, pady=5, sticky="e")
        
        # 重置为默认Prompt按钮
        ttk.Button(prompt_frame, text="重置为默认", command=self.app.reset_to_default_prompt).grid(row=4, column=1, padx=5, pady=5, sticky="e")
        
        # 操作区域 - 使用滚动条
        action_frame = ttk.LabelFrame(left_frame, text="操作")
        action_frame.pack(fill="x")
        
        # 创建画布和滚动条
        canvas = tk.Canvas(action_frame)
        scrollbar = ttk.Scrollbar(action_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 按钮布局为一行3个
        # 第一行
        ttk.Button(scrollable_frame, text="获取卡片", command=self.app.fetch_cards).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(scrollable_frame, text="预览标签", command=self.app.preview_tags).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(scrollable_frame, text="添加标签", command=self.app.add_tags).grid(row=0, column=2, padx=5, pady=5)
        
        # 第二行
        ttk.Button(scrollable_frame, text="清理标签", command=self.app.clear_tags).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(scrollable_frame, text="暂停", command=self.app.pause_process).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(scrollable_frame, text="停止", command=self.app.stop_process).grid(row=1, column=2, padx=5, pady=5)
        
        # 第三行
        ttk.Button(scrollable_frame, text="校对标签", command=self.app.check_tags).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(scrollable_frame, text="修正标签", command=self.app.fix_tags).grid(row=2, column=1, padx=5, pady=5)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(right_frame, text="预览结果")
        result_frame.pack(fill="both", expand=True)
        
        # 创建水平和垂直滚动条
        hscrollbar = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL)
        vscrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)
        
        # 表格
        columns = ("card_id", "front", "back", "tags", "校正结果")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", 
                                xscrollcommand=hscrollbar.set, yscrollcommand=vscrollbar.set)
        
        # 配置列
        self.tree.heading("card_id", text="卡片ID")
        self.tree.heading("front", text="正面")
        self.tree.heading("back", text="背面")
        self.tree.heading("tags", text="现有标签")
        self.tree.heading("校正结果", text="校正结果")
        
        self.tree.column("card_id", width=100)
        self.tree.column("front", width=180)
        self.tree.column("back", width=180)
        self.tree.column("tags", width=250)  # 调整标签列宽度
        self.tree.column("校正结果", width=200)  # 新增校正结果列
        
        # 配置滚动条
        hscrollbar.config(command=self.tree.xview)
        vscrollbar.config(command=self.tree.yview)
        
        # 布局
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill="both", expand=True)
        
        # 初始化Prompt列表 - 移到AnkiTagger类中初始化