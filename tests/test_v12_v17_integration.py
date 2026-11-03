# -*- coding: utf-8 -*-
"""
V12-V17 集成验证测试
====================
验证六个新模块的跨模块协同：
  V12 butler_os + quartet_director_pack
  V13 vector_sea_explorer + vector_sea_pack
  V14 skill_lathe + protocol_plugins
  V15 dehallucination + dehallucination_pack
  V16 router_layer + event_filter + external_watchdog + super_agent_pack
  V17 memory_of_yuan（独立于holoaeon源码，单独测试）
"""
import json
import os
import sys
import unittest
from io import StringIO
from contextlib import redirect_stdout


class TestV12ButlerOS(unittest.TestCase):
    """V12 管家OS + 四人组扩展包"""

    def test_butler_os_import(self):
        """butler_os模块可导入"""
        from holoaeon.butler_os import main
        self.assertTrue(callable(main))

    def test_quartet_director_pack_registered(self):
        """quartet_director在第13扩展包注册"""
        from holoaeon.packs import EXTRA_PACK_ORDER
        self.assertIn("quartet_director", EXTRA_PACK_ORDER)

    def test_quartet_director_pack_loadable(self):
        """quartet_director包可加载"""
        from holoaeon.packs import get_extra_pack
        pack = get_extra_pack("quartet_director")
        self.assertIsNotNone(pack)
        self.assertTrue(len(pack.skills) > 0)


class TestV13VectorSea(unittest.TestCase):
    """V13 向量海勘探平台"""

    def test_vector_sea_explorer_import(self):
        """vector_sea_explorer模块可导入（函数式 API：explore/vector_match）"""
        import holoaeon.vector_sea_explorer as vse
        self.assertTrue(hasattr(vse, 'explore'))
        self.assertTrue(callable(vse.vector_match))

    def test_vector_sea_pack_registered(self):
        """vector_sea在第14扩展包注册"""
        from holoaeon.packs import EXTRA_PACK_ORDER
        self.assertIn("vector_sea", EXTRA_PACK_ORDER)


class TestV14SkillLatheProtocol(unittest.TestCase):
    """V14 技能机床 + 协议插件"""

    def test_skill_lathe_import(self):
        """skill_lathe模块可导入"""
        from holoaeon.skill_lathe import SkillLathe
        self.assertTrue(hasattr(SkillLathe, '__init__'))

    def test_protocol_plugins_import(self):
        """protocol_plugins模块可导入（export_skill_to_protocol/list_protocols）"""
        import holoaeon.protocol_plugins as pp
        self.assertTrue(callable(pp.export_skill_to_protocol))
        self.assertTrue(callable(pp.list_protocols))


class TestV15Dehallucination(unittest.TestCase):
    """V15 去幻觉模块"""

    def test_dehallucination_import(self):
        """dehallucination模块可导入"""
        from holoaeon.dehallucination import DeHallucinationModule
        self.assertTrue(hasattr(DeHallucinationModule, '__init__'))

    def test_dehallucination_pack_registered(self):
        """dehallucination在第15扩展包注册"""
        from holoaeon.packs import EXTRA_PACK_ORDER
        self.assertIn("dehallucination", EXTRA_PACK_ORDER)

    def test_dehallucination_check(self):
        """去幻觉检查返回结构正确"""
        from holoaeon.dehallucination import DeHallucinationModule
        dh = DeHallucinationModule(fetch_callback=None)
        result = dh.check("测试文本")
        self.assertIsInstance(result, dict)
        self.assertIn("verdict", result)


class TestV16SuperAgent(unittest.TestCase):
    """V16 超级智能体蒸馏"""

    def test_router_layer_import(self):
        """router_layer模块可导入"""
        from holoaeon.router_layer import RouterLayer
        self.assertTrue(hasattr(RouterLayer, '__init__'))

    def test_event_filter_import(self):
        """event_filter模块可导入"""
        from holoaeon.event_filter import EventFilter
        self.assertTrue(hasattr(EventFilter, '__init__'))

    def test_external_watchdog_import(self):
        """external_watchdog模块可导入"""
        from holoaeon.external_watchdog import ExternalWatchdog
        self.assertTrue(hasattr(ExternalWatchdog, '__init__'))

    def test_super_agent_pack_registered(self):
        """super_agent在第16扩展包注册"""
        from holoaeon.packs import EXTRA_PACK_ORDER
        self.assertIn("super_agent", EXTRA_PACK_ORDER)

    def test_router_dispatch(self):
        """RouterLayer分派返回字符串"""
        from holoaeon.router_layer import RouterLayer
        router = RouterLayer()
        result = router.receive("测试任务")
        self.assertIsNotNone(result)


class TestV17MemoryOfYuan(unittest.TestCase):
    """V17 玉安记忆之王（独立于holoaeon源码）"""

    def test_memory_import(self):
        """memory_of_yuan可全域导入"""
        try:
            import memory_of_yuan as moy
            self.assertTrue(hasattr(moy, 'status'))
        except ImportError:
            self.skipTest("memory_of_yuan未安装（V17未执行）")

    def test_memory_status(self):
        """status()返回正确结构"""
        try:
            import memory_of_yuan as moy
            s = moy.status()
            self.assertEqual(s["module"], "memory_of_yuan")
            self.assertEqual(s["name"], "玉安记忆之王")
        except ImportError:
            self.skipTest("memory_of_yuan未安装（V17未执行）")

    def test_memory_holographic_query(self):
        """holographic_query返回共振结果"""
        try:
            import memory_of_yuan as moy
            r = moy.holographic_query("holoaeon")
            self.assertIsInstance(r, dict)
            self.assertIn("resonance_count", r)
        except ImportError:
            self.skipTest("memory_of_yuan未安装（V17未执行）")


class TestCrossModuleIntegration(unittest.TestCase):
    """跨模块集成测试——验证V12-V16模块在Kernel中协同"""

    def test_all_extra_packs_loadable(self):
        """全部17个扩展包可加载（V19 16→17 +concept_anatomy）"""
        from holoaeon.packs import all_extra_packs
        packs = all_extra_packs()
        self.assertEqual(len(packs), 17)

    def test_kernel_with_all_packs(self):
        """装齐全部扩展包的Kernel可submit"""
        from holoaeon.kernel import Kernel
        from holoaeon.packs import PACK_ORDER, get_pack, all_extra_packs
        kernel = Kernel()
        for key in PACK_ORDER:
            get_pack(key).install(kernel)
        for pack in all_extra_packs():
            pack.install(kernel)
        # 提交一个简单任务验证不崩溃
        result = kernel.submit("data.describe", args={"src": "dummy"})
        self.assertIsInstance(result, dict)

    def test_extra_pack_order_sequence(self):
        """EXTRA_PACK_ORDER顺序正确（V12-V16新增包在正确位置）"""
        from holoaeon.packs import EXTRA_PACK_ORDER
        # V8前10个 + V8 tcm_rehab + V9 topology_resonance + V12 quartet_director
        # + V14 vector_sea + V15 dehallucination + V16 super_agent
        expected_new = [
            "topology_resonance",  # V9 (12th)
            "quartet_director",    # V12 (13th)
            "vector_sea",          # V14 (14th)
            "dehallucination",     # V15 (15th)
            "super_agent",         # V16 (16th)
        ]
        for i, key in enumerate(expected_new):
            idx = EXTRA_PACK_ORDER.index(key)
            # 每个新包应该在前一个之后
            if i > 0:
                prev_idx = EXTRA_PACK_ORDER.index(expected_new[i-1])
                self.assertGreater(idx, prev_idx,
                    f"{key}应在{expected_new[i-1]}之后")

    def test_butler_os_menu_has_all_modules(self):
        """butler_os菜单包含V12-V16所有模块入口"""
        from holoaeon import butler_os
        # butler_os的菜单应该引用了所有新模块
        source = open(butler_os.__file__, encoding='utf-8').read()
        # V13 向量海
        self.assertTrue('vector_sea' in source or 'explore' in source.lower())
        # V15 去幻觉
        self.assertTrue('dehallucination' in source or '幻觉' in source)
        # V16 超级智能体
        self.assertTrue('router' in source or 'super_agent' in source or '自主' in source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
