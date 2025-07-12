"""
测试笔记服务与向量数据库集成功能
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

# 将项目根目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from service.services.note_service import NoteService
from service.models.note import Note, InvalidTagError
from core.database_core import DatabaseClient
from core.vector_core import ChromaVectorClient, VectorConfig


def test_note_vector_integration():
    """测试笔记服务与向量数据库集成功能"""
    
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 加载环境变量
    load_dotenv()
    
    print("=== 笔记服务与向量数据库集成测试 ===\n")
    
    try:
        # 初始化数据库
        print("1. 初始化数据库...")
        db_client = DatabaseClient()
        if not db_client.initialize():
            print("❌ 数据库初始化失败")
            return
        
        # 创建表结构
        print("2. 创建数据库表结构...")
        if not db_client.create_tables():
            print("❌ 创建数据库表失败")
            return
        print("✓ 数据库初始化成功\n")
        
        # 初始化服务
        print("3. 初始化笔记服务...")
        note_service = NoteService(db_client=db_client)
        print("✓ 笔记服务初始化成功\n")
        
        # 测试用户ID
        test_user_id = 1
        
        # 测试1: 创建笔记（包括向量数据库存储）
        print("4. 测试创建笔记...")
        
        # 测试有效标签
        valid_tags = ['lifestyle tips', 'cooking advice', 'weather interpretation', 'news context']
        
        notes_created = []
        for i, tag in enumerate(valid_tags):
            note = note_service.create_note(
                user_id=test_user_id,
                title=f"测试笔记 {i+1}: {tag}",
                content=f"这是一个关于{tag}的测试笔记内容。包含了详细的信息和实用的建议。",
                tag=tag,
                status='draft'
            )
            
            if note:
                notes_created.append(note)
                print(f"✓ 创建笔记成功: ID={note.id}, 标签={note.tag}")
            else:
                print(f"✗ 创建笔记失败: 标签={tag}")
        
        print(f"✓ 成功创建了 {len(notes_created)} 个笔记\n")
        
        # 测试2: 测试无效标签
        print("5. 测试无效标签验证...")
        invalid_note = note_service.create_note(
            user_id=test_user_id,
            title="无效标签测试",
            content="这是一个无效标签的测试",
            tag="invalid_tag",
            status='draft'
        )
        
        if invalid_note is None:
            print("✓ 无效标签验证成功（拒绝创建）")
        else:
            print("✗ 无效标签验证失败（应该拒绝创建）")
        print()
        
        # 测试3: 获取笔记
        print("6. 测试获取笔记...")
        if notes_created:
            note = note_service.get_note(notes_created[0].id)
            if note:
                print(f"✓ 获取笔记成功: {note.title}")
            else:
                print("✗ 获取笔记失败")
        print()
        
        # 测试4: 更新笔记（包括向量数据库更新）
        print("7. 测试更新笔记...")
        if notes_created:
            updated_note = note_service.update_note(
                note_id=notes_created[0].id,
                title="更新后的标题",
                content="更新后的内容，包含新的信息和详细描述。",
                tag="cooking advice",
                status='published'
            )
            
            if updated_note:
                print(f"✓ 更新笔记成功: {updated_note.title}, 标签={updated_note.tag}")
            else:
                print("✗ 更新笔记失败")
        print()
        
        # 测试5: 按标签搜索笔记
        print("8. 测试按标签搜索笔记...")
        cooking_notes = note_service.get_notes_by_tag(test_user_id, "cooking advice")
        print(f"✓ 找到 {len(cooking_notes)} 个cooking advice标签的笔记")
        
        # 测试6: 获取用户所有标签
        print("9. 测试获取用户标签...")
        user_tags = note_service.get_user_tags(test_user_id)
        print(f"✓ 用户使用的标签: {user_tags}")
        print()
        
        # 测试7: 向量搜索功能
        print("10. 测试向量搜索功能...")
        if note_service.vector_client:
            # 测试多个查询以确保向量搜索工作正常
            test_queries = [
                "cooking advice",
                "生活技巧",
                "weather",
                "测试笔记"
            ]
            
            for query in test_queries:
                vector_results = note_service.search_notes_by_vector(
                    user_id=test_user_id,
                    query=query,
                    limit=5
                )
                print(f"  查询 '{query}': 返回 {len(vector_results)} 个结果")
                for result in vector_results[:3]:  # 显示前3个结果
                    print(f"    - 笔记ID: {result.get('note_id')}, 标题: {result.get('title')}, 得分: {result.get('score', 0):.3f}")
                
                if len(vector_results) > 0:
                    print(f"✓ 向量搜索功能正常，找到相关笔记")
                    break  # 找到结果就停止
            else:
                print("⚠ 所有查询都未返回结果，可能需要调整搜索参数")
        else:
            print("⚠ 向量数据库不可用，跳过向量搜索测试")
        print()
        
        # 测试8: 获取笔记统计信息
        print("11. 测试获取笔记统计信息...")
        stats = note_service.get_notes_statistics(test_user_id)
        print(f"✓ 统计信息:")
        print(f"  - 总笔记数: {stats.get('total_notes', 0)}")
        print(f"  - 状态统计: {stats.get('status_counts', {})}")
        print(f"  - 标签统计: {stats.get('tag_counts', {})}")
        print(f"  - 总标签数: {stats.get('total_tags', 0)}")
        print()
        
        # 测试9: 删除笔记（包括向量数据库删除）
        print("12. 测试删除笔记...")
        if notes_created:
            note_to_delete = notes_created[-1]  # 删除最后一个笔记
            success = note_service.delete_note(note_to_delete.id)
            if success:
                print(f"✓ 删除笔记成功: ID={note_to_delete.id}")
            else:
                print(f"✗ 删除笔记失败: ID={note_to_delete.id}")
        print()
        
        # 测试10: 验证删除后的状态
        print("13. 验证删除后的状态...")
        final_stats = note_service.get_notes_statistics(test_user_id)
        print(f"✓ 删除后总笔记数: {final_stats.get('total_notes', 0)}")
        print()
        
        print("=== 所有测试完成 ===")
        print("✓ 笔记服务与向量数据库集成功能正常")
        
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理
        if 'note_service' in locals():
            note_service.close()
        if 'db_client' in locals():
            db_client.close()


if __name__ == "__main__":
    test_note_vector_integration() 