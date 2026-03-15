import tkinter as tk
from tkinter import messagebox
import threading
import time
from modules.config import ConfigManager
from modules.anki import AnkiConnect
from modules.ai import AIClient
from modules.ui import UIManager

class AnkiTagger:
    def __init__(self, root):
        self.root = root
        self.root.title("Anki AI标签添加器")
        self.root.geometry("1000x700")
        
        # 初始化配置管理器
        self.config = ConfigManager()
        
        # 初始化AnkiConnect
        self.anki = AnkiConnect()
        
        # 初始化AI客户端
        self.ai_client = None
        
        # API地址选项
        self.api_options = {
            "硅基流动": "https://api.siliconflow.cn/v1/chat/completions",
            "Gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        }
        
        # 卡片数据
        self.cards = []
        
        # 线程控制
        self.running = False
        self.paused = False
        
        # 初始化UI
        self.ui = UIManager(self.root, self)
        
        # 初始化AI客户端
        self.update_ai_client()
        
        # 加载保存的模型列表
        self.load_saved_models()
        
        # 初始化Prompt列表
        self.refresh_prompts()
    
    def update_ai_client(self):
        """更新AI客户端"""
        api_key = self.ui.api_key_var.get()
        api_base = self.ui.api_base_var.get()
        self.ai_client = AIClient(api_key, api_base)
    
    def on_api_key_change(self, *args):
        """API Key变化时的处理"""
        self.config.set_api_key(self.ui.api_key_var.get())
        self.update_ai_client()
    
    def on_api_base_change(self, *args):
        """API Base变化时的处理"""
        api_base = self.ui.api_base_var.get()
        self.config.set_api_base(api_base)
        self.update_ai_client()
        
        # 检查是否匹配预设的API服务
        matched = False
        for service, url in self.api_options.items():
            if api_base == url:
                self.ui.api_service_var.set(service)
                matched = True
                break
        
        # 如果不匹配，设置为自定义
        if not matched:
            self.ui.api_service_var.set("自定义")
    
    def on_model_change(self, *args):
        """模型变化时的处理"""
        self.config.set_model(self.ui.model_var.get())
    
    def on_model_search(self, *args):
        """模型搜索功能"""
        search_term = self.ui.model_search_var.get().lower()
        
        if not hasattr(self, 'all_models'):
            # 如果还没有获取模型列表，先获取
            return
        
        all_models = self.all_models
        
        if not search_term:
            # 显示所有模型
            self.ui.model_combobox['values'] = all_models
        else:
            # 过滤模型
            filtered_models = [model for model in all_models if search_term in model.lower()]
            self.ui.model_combobox['values'] = filtered_models
        
        # 保持当前选中的模型
        current_model = self.ui.model_var.get()
        if current_model:
            self.ui.model_var.set(current_model)
    
    def on_model_search_button(self):
        """模型搜索按钮点击事件"""
        self.on_model_search()
    
    def on_api_service_change(self, event):
        """API服务选择变化时的处理"""
        service = self.ui.api_service_var.get()
        if service in self.api_options:
            self.ui.api_base_var.set(self.api_options[service])
        # 自定义选项保持当前值不变
    
    def refresh_prompts(self):
        """刷新Prompt列表"""
        prompts = self.config.get_prompts()
        self.ui.prompt_combobox['values'] = list(prompts.keys())
        if prompts:
            self.ui.prompt_name_var.set(list(prompts.keys())[0])
            self.ui.prompt_text.delete(1.0, tk.END)
            self.ui.prompt_text.insert(tk.END, prompts[list(prompts.keys())[0]])
    
    def on_prompt_change(self, event):
        """Prompt选择变化时的处理"""
        prompt_name = self.ui.prompt_name_var.get()
        prompts = self.config.get_prompts()
        if prompt_name in prompts:
            self.ui.prompt_text.delete(1.0, tk.END)
            self.ui.prompt_text.insert(tk.END, prompts[prompt_name])
    
    def save_current_prompt(self):
        """保存当前Prompt"""
        prompt_name = self.ui.prompt_name_var.get()
        prompt_content = self.ui.prompt_text.get(1.0, tk.END).strip()
        
        if not prompt_name:
            messagebox.showerror("错误", "请输入Prompt名称")
            return
        
        if not prompt_content:
            messagebox.showerror("错误", "Prompt内容不能为空")
            return
        
        self.config.add_prompt(prompt_name, prompt_content)
        self.refresh_prompts()
        messagebox.showinfo("成功", "Prompt保存成功")
    
    def delete_current_prompt(self):
        """删除当前Prompt"""
        prompt_name = self.ui.prompt_name_var.get()
        
        if not prompt_name:
            messagebox.showerror("错误", "请选择要删除的Prompt")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除Prompt '{prompt_name}'吗？"):
            return
        
        self.config.remove_prompt(prompt_name)
        self.refresh_prompts()
        messagebox.showinfo("成功", "Prompt删除成功")
    
    def reset_to_default_prompt(self):
        """重置为默认Prompt"""
        default_prompt = self.config.get_default_prompt()
        self.ui.prompt_text.delete(1.0, tk.END)
        self.ui.prompt_text.insert(tk.END, default_prompt)
        messagebox.showinfo("成功", "已重置为默认Prompt")
    
    def load_saved_models(self):
        """加载保存的模型列表"""
        models = self.config.get_models()
        if models:
            self.all_models = models
            self.ui.model_combobox['values'] = models
    
    def fetch_models(self):
        """获取可用的模型列表"""
        self.update_ai_client()
        models = self.ai_client.get_models()
        
        if models:
            # 保存完整的模型列表
            self.all_models = models
            self.ui.model_combobox['values'] = models
            # 保存到配置文件
            self.config.set_models(models)
            messagebox.showinfo("成功", f"获取到 {len(models)} 个模型")
        else:
            messagebox.showerror("错误", "获取模型列表失败")
    
    def fetch_decks(self):
        """获取所有牌组列表"""
        decks = self.anki.get_decks()
        
        if decks:
            self.ui.deck_combobox['values'] = ["所有牌组"] + decks
            # 默认选择第一个牌组
            if decks:
                self.ui.deck_var.set(decks[0])
            messagebox.showinfo("成功", f"获取到 {len(decks)} 个牌组")
        else:
            messagebox.showinfo("提示", "获取牌组列表失败")
    
    def fetch_cards(self):
        """获取指定牌组的卡片"""
        # 清空表格
        for item in self.ui.tree.get_children():
            self.ui.tree.delete(item)
        
        # 获取卡片数量
        card_count_str = self.ui.card_count_var.get()
        
        # 构建查询语句
        deck_name = self.ui.deck_var.get()
        if deck_name == "所有牌组":
            query = ""
        else:
            query = f"deck:{deck_name}"
        
        # 获取卡片ID
        card_ids = self.anki.find_cards(query)
        if not card_ids:
            messagebox.showinfo("提示", "没有找到卡片")
            return
        
        # 处理卡片数量
        if card_count_str != "全部":
            try:
                card_count = int(card_count_str)
                card_ids = card_ids[:card_count]  # 取前面的卡片，获取最新的卡片
            except ValueError:
                messagebox.showerror("错误", "请选择有效的卡片数量")
                return
        
        # 获取卡片信息（已修复标签解析）
        self.cards = self.anki.get_cards_info(card_ids)
        if not self.cards:
            messagebox.showinfo("提示", "获取卡片信息失败")
            return
        
        # 标签筛选
        tag_filter = self.ui.tag_filter_var.get()
        filtered_cards = []
        
        # 获取自定义筛选字符
        custom_tag = self.ui.custom_tag_var.get().strip().lower()
        
        for card in self.cards:
            # 修复：使用解析后的标签列表
            tags = card.get("tags_list", [])
            if tag_filter == "全部卡片":
                filtered_cards.append(card)
            elif tag_filter == "有标签的卡片" and tags:
                filtered_cards.append(card)
            elif tag_filter == "无标签的卡片" and not tags:
                filtered_cards.append(card)
            elif tag_filter == "自定义筛选" and custom_tag:
                # 检查是否有标签包含自定义字符
                for tag in tags:
                    if custom_tag in tag.lower():
                        filtered_cards.append(card)
                        break
        
        self.cards = filtered_cards
        
        if not self.cards:
            messagebox.showinfo("提示", "没有符合条件的卡片")
            return
        
        # 显示卡片
        for card in self.cards:
            content = self.anki.get_card_content(card)
            # 提取前两个字段作为正面和背面显示
            lines = content.split("\n")
            front = lines[0] if lines else ""
            back = lines[1] if len(lines) > 1 else ""
            # 清理HTML标签
            front = self.ai_client.clean_html(front)
            back = self.ai_client.clean_html(back)
            # 修复：正确显示标签（列表转逗号分隔字符串）
            tags = card.get("tags_list", [])
            tags_str = ", ".join(tags) if tags else "无"
            self.ui.tree.insert("", tk.END, values=(card["cardId"], front[:50] + "..." if len(front) > 50 else front, back[:50] + "..." if len(back) > 50 else back, tags_str, ""))
        
    def preview_tags(self):
        """预览标签生成结果"""
        if not self.cards:
            messagebox.showinfo("提示", "请先获取卡片")
            return
        
        # 清空标签列
        for item in self.ui.tree.get_children():
            self.ui.tree.set(item, "tags", "生成中...")
        
        # 线程处理，避免UI卡顿
        def process_cards():
            # 只预览前5张卡片
            preview_cards = self.cards[:5]
            
            for i, card in enumerate(preview_cards):
                try:
                    # 获取卡片内容（动态字段，清理HTML）
                    content = self.anki.get_card_content(card)
                    clean_content = self.ai_client.clean_html(content)
                    
                    # 生成标签
                    prompt = self.ui.prompt_text.get(1.0, tk.END).strip()
                    tags = self.ai_client.generate_tags(clean_content, self.ui.model_var.get(), prompt)
                    
                    # 更新UI
                    self.root.after(0, lambda i=i, tags=tags: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", ", ".join(tags)))
                    self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", ""))
                    
                    # 延迟，避免API限流
                    time.sleep(1)
                except Exception as e:
                    # 捕获异常，确保线程不会死掉
                    self.root.after(0, lambda i=i, e=e: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", f"错误: {str(e)}"))
                    self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", "错误"))
                    time.sleep(1)
            
            # 完成提示
            self.root.after(0, lambda: messagebox.showinfo("成功", "标签预览完成，仅显示前5张卡片的结果"))
        
        # 启动线程
        threading.Thread(target=process_cards, daemon=True).start()
    
    def add_tags(self):
        """为卡片添加标签"""
        if not self.cards:
            messagebox.showinfo("提示", "请先获取卡片")
            return
        
        # 清空标签列
        for item in self.ui.tree.get_children():
            self.ui.tree.set(item, "tags", "生成中...")
        
        # 重置线程控制
        self.running = True
        self.paused = False
        
        # 线程处理，避免UI卡顿
        def process_cards():
            try:
                for i, card in enumerate(self.cards):
                    try:
                        # 检查是否停止
                        if not self.running:
                            break
                        
                        # 检查是否暂停
                        while self.paused:
                            time.sleep(0.1)
                        
                        # 获取卡片内容（动态字段，清理HTML）
                        content = self.anki.get_card_content(card)
                        clean_content = self.ai_client.clean_html(content)
                        
                        # 生成标签
                        prompt = self.ui.prompt_text.get(1.0, tk.END).strip()
                        tags = self.ai_client.generate_tags(clean_content, self.ui.model_var.get(), prompt)
                        
                        # 更新UI
                        self.root.after(0, lambda i=i, tags=tags: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", ", ".join(tags)))
                        self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", ""))
                        
                        # 添加标签到笔记（标签属于笔记，而非卡片）
                        if tags and tags[0] != "生成失败" and not tags[0].startswith("错误"):
                            note_id = card.get("note")
                            if note_id:
                                # 修正：AnkiConnect 的 addTags 推荐使用空格分隔或直接传 list
                                tag_string = " ".join(tags)
                                self.anki.add_tags([note_id], tag_string)
                        
                        # 延迟，避免API限流
                        time.sleep(0.5)  # 减少延迟，提高速度
                    except Exception as e:
                        # 捕获异常，确保线程不会死掉
                        self.root.after(0, lambda i=i, e=e: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", f"错误: {str(e)}"))
                        self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", "错误"))
                        time.sleep(0.5)
            finally:
                # 完成提示
                if self.running:
                    self.root.after(0, lambda: messagebox.showinfo("成功", "标签添加完成"))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("提示", "标签添加已停止"))
        
        # 启动线程
        threading.Thread(target=process_cards, daemon=True).start()
    
    def clear_tags(self):
        """清理卡片标签"""
        if not self.cards:
            messagebox.showinfo("提示", "请先获取卡片")
            return
        
        # 确认清理
        if not messagebox.askyesno("确认", "确定要清理选中卡片的所有标签吗？"):
            return
        
        # 重置线程控制
        self.running = True
        self.paused = False
        
        # 线程处理，避免UI卡顿
        def process_cards():
            try:
                for i, card in enumerate(self.cards):
                    try:
                        # 检查是否停止
                        if not self.running:
                            break
                        
                        # 检查是否暂停
                        while self.paused:
                            time.sleep(0.1)
                        
                        # 清理标签
                        note_id = card.get("note")
                        if note_id:
                            # 获取现有标签
                            tags = card.get("tags_list", [])
                            if tags:
                                # 移除所有标签
                                tag_string = " ".join(tags)
                                self.anki.remove_tags([note_id], tag_string)
                        
                        # 更新UI
                        self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", "无"))
                        self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", ""))
                        
                        # 延迟，避免API限流
                        time.sleep(0.2)  # 减少延迟，提高速度
                    except Exception as e:
                        # 捕获异常，确保线程不会死掉
                        self.root.after(0, lambda i=i, e=e: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", f"错误: {str(e)}"))
                        self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", "错误"))
                        time.sleep(0.2)
            finally:
                # 完成提示
                if self.running:
                    self.root.after(0, lambda: messagebox.showinfo("成功", "标签清理完成"))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("提示", "标签清理已停止"))
        
        # 启动线程
        threading.Thread(target=process_cards, daemon=True).start()
    
    def pause_process(self):
        """暂停处理"""
        self.paused = not self.paused
        messagebox.showinfo("提示", "处理已" + ("暂停" if self.paused else "继续"))
    
    def stop_process(self):
        """停止处理"""
        self.running = False
        self.paused = False
        messagebox.showinfo("提示", "处理已停止")
    
    def check_tags(self):
        """校对标签"""
        if not self.cards:
            messagebox.showinfo("提示", "请先获取卡片")
            return
        
        # 清空标签列
        for item in self.ui.tree.get_children():
            self.ui.tree.set(item, "tags", "校对中...")
        
        # 重置线程控制
        self.running = True
        self.paused = False
        
        # 线程处理，避免UI卡顿
        def process_cards():
            try:
                for i, card in enumerate(self.cards):
                    try:
                        # 检查是否停止
                        if not self.running:
                            break
                        
                        # 检查是否暂停
                        while self.paused:
                            time.sleep(0.1)
                        
                        # 获取卡片内容（动态字段，清理HTML）
                        content = self.anki.get_card_content(card)
                        clean_content = self.ai_client.clean_html(content)
                        
                        # 获取现有标签
                        current_tags = card.get("tags_list", [])
                        
                        # 生成新标签
                        prompt = self.ui.prompt_text.get(1.0, tk.END).strip()
                        new_tags = self.ai_client.generate_tags(clean_content, self.ui.model_var.get(), prompt)
                        
                        # 比较标签
                        if set(current_tags) != set(new_tags):
                            # 显示差异
                            tags_str = f"当前: {', '.join(current_tags)}\n建议: {', '.join(new_tags)}"
                            fix_result = f"需要修改: {', '.join(new_tags)}"
                        else:
                            tags_str = f"当前: {', '.join(current_tags)}"
                            fix_result = "true"
                        
                        # 更新UI
                        self.root.after(0, lambda i=i, tags_str=tags_str: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", tags_str))
                        self.root.after(0, lambda i=i, fix_result=fix_result: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", fix_result))
                        
                        # 延迟，避免API限流
                        time.sleep(0.5)
                    except Exception as e:
                        # 捕获异常，确保线程不会死掉
                        self.root.after(0, lambda i=i, e=e: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", f"错误: {str(e)}"))
                        self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", "错误"))
                        time.sleep(0.5)
            finally:
                # 完成提示
                if self.running:
                    self.root.after(0, lambda: messagebox.showinfo("成功", "标签校对完成，请查看建议修改"))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("提示", "标签校对已停止"))
        
        # 启动线程
        threading.Thread(target=process_cards, daemon=True).start()
    
    def fix_tags(self):
        """修正标签"""
        if not self.cards:
            messagebox.showinfo("提示", "请先获取卡片")
            return
        
        # 确认修正
        if not messagebox.askyesno("确认", "确定要根据校对结果修正标签吗？"):
            return
        
        # 清空标签列
        for item in self.ui.tree.get_children():
            self.ui.tree.set(item, "tags", "修正中...")
        
        # 重置线程控制
        self.running = True
        self.paused = False
        
        # 线程处理，避免UI卡顿
        def process_cards():
            try:
                for i, card in enumerate(self.cards):
                    try:
                        # 检查是否停止
                        if not self.running:
                            break
                        
                        # 检查是否暂停
                        while self.paused:
                            time.sleep(0.1)
                        
                        # 获取校正结果
                        tree_item = self.ui.tree.get_children()[i]
                        fix_result = self.ui.tree.set(tree_item, "校正结果")
                        
                        # 只修正需要修改的卡片
                        if fix_result != "true":
                            # 获取卡片内容（动态字段，清理HTML）
                            content = self.anki.get_card_content(card)
                            clean_content = self.ai_client.clean_html(content)
                            
                            # 生成新标签
                            prompt = self.ui.prompt_text.get(1.0, tk.END).strip()
                            new_tags = self.ai_client.generate_tags(clean_content, self.ui.model_var.get(), prompt)
                            
                            # 添加标签到笔记（标签属于笔记，而非卡片）
                            if new_tags and new_tags[0] != "生成失败" and not new_tags[0].startswith("错误"):
                                note_id = card.get("note")
                                if note_id:
                                    # 先清理现有标签
                                    current_tags = card.get("tags_list", [])
                                    if current_tags:
                                        tag_string = " ".join(current_tags)
                                        self.anki.remove_tags([note_id], tag_string)
                                    # 添加新标签
                                    tag_string = " ".join(new_tags)
                                    self.anki.add_tags([note_id], tag_string)
                            
                            # 更新UI
                            self.root.after(0, lambda i=i, new_tags=new_tags: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", ", ".join(new_tags)))
                            self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", "已修正"))
                        else:
                            # 跳过无需修改的卡片
                            self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", "无需修改"))
                        
                        # 延迟，避免API限流
                        time.sleep(0.5)
                    except Exception as e:
                        # 捕获异常，确保线程不会死掉
                        self.root.after(0, lambda i=i, e=e: self.ui.tree.set(self.ui.tree.get_children()[i], "tags", f"错误: {str(e)}"))
                        self.root.after(0, lambda i=i: self.ui.tree.set(self.ui.tree.get_children()[i], "校正结果", "错误"))
                        time.sleep(0.5)
            finally:
                # 完成提示
                if self.running:
                    self.root.after(0, lambda: messagebox.showinfo("成功", "标签修正完成"))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("提示", "标签修正已停止"))
        
        # 启动线程
        threading.Thread(target=process_cards, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AnkiTagger(root)
    root.mainloop()