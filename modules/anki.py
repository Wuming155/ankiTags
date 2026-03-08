import requests
import tkinter as tk
from tkinter import messagebox

class AnkiConnect:
    def __init__(self, host="http://localhost", port=8765):
        self.base_url = f"{host}:{port}"
    
    def request(self, action, **params):
        """向AnkiConnect发送请求，增加错误信息返回"""
        try:
            response = requests.post(
                self.base_url,
                json={"action": action, "params": params, "version": 6}
            )
            response.raise_for_status()  # 抛出HTTP错误
            result = response.json()
            if "error" in result and result["error"] is not None:
                messagebox.showerror("AnkiConnect错误", f"{action}失败: {result['error']}")
                return None
            return result
        except requests.exceptions.RequestException as e:
            messagebox.showerror("错误", f"AnkiConnect连接失败: {str(e)}")
            return None
    
    def get_decks(self):
        """获取所有牌组"""
        result = self.request("deckNames")
        if result and result.get("result"):
            return result["result"]
        return []
    
    def find_cards(self, query=""):
        """根据查询条件查找卡片"""
        result = self.request("findCards", query=query)
        if result and result.get("result"):
            return result["result"]
        return []
    
    def get_cards_info(self, card_ids):
        """获取卡片信息，正确解析标签（字符串转列表）"""
        result = self.request("cardsInfo", cards=card_ids)
        if not result or not result.get("result"):
            return []
        
        cards = result["result"]
        
        # 获取所有笔记ID
        note_ids = list(set(card.get("note", 0) for card in cards))
        note_ids = [nid for nid in note_ids if nid > 0]
        
        # 获取笔记信息，包含标签
        note_info = {}
        if note_ids:
            notes_result = self.request("notesInfo", notes=note_ids)
            if notes_result and notes_result.get("result"):
                for note in notes_result["result"]:
                    note_info[note.get("noteId")] = note.get("tags", [])
        
        # 为每个卡片添加标签信息
        for card in cards:
            note_id = card.get("note")
            tags = note_info.get(note_id, [])
            # 确保tags是列表
            if isinstance(tags, str):
                tags = tags.split()
            card["tags_list"] = tags
        
        return cards
    
    def add_tags(self, note_ids, tags):
        """
        为笔记添加标签
        :param note_ids: 笔记ID列表
        :param tags: 标签列表或空格分隔的字符串
        :return: 是否成功
        """
        if isinstance(tags, list):
            tags = " ".join(tags)  # 转为Anki支持的空格分隔格式
        result = self.request("addTags", notes=note_ids, tags=tags)
        return result is not None
    
    def remove_tags(self, note_ids, tags):
        """
        从笔记中移除标签
        :param note_ids: 笔记ID列表
        :param tags: 标签列表或空格分隔的字符串
        :return: 是否成功
        """
        if isinstance(tags, list):
            tags = " ".join(tags)
        result = self.request("removeTags", notes=note_ids, tags=tags)
        return result is not None
    
    def get_card_content(self, card):
        """获取卡片内容"""
        fields = card.get("fields", {})
        content = []
        for field_name, field_data in fields.items():
            field_value = field_data.get("value", "")
            if field_value.strip():
                content.append(f"{field_name}: {field_value}")
        return "\n".join(content)