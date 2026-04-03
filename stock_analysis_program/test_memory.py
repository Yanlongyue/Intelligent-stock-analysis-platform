from src.memory_manager import MemoryManager
mm = MemoryManager()
rules = mm.load_memory_rules()
print('规则数量:', len(rules))
