#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
 .name = KBUILD_MODNAME,
 .init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
 .exit = cleanup_module,
#endif
 .arch = MODULE_ARCH_INIT,
};

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0xae141548, "module_layout" },
	{ 0x4302d0eb, "free_pages" },
	{ 0x3c2c5af5, "sprintf" },
	{ 0xb742fd7, "simple_strtol" },
	{ 0xe2d5255a, "strcmp" },
	{ 0xd17d35b3, "d_path" },
	{ 0x93fca811, "__get_free_pages" },
	{ 0xf77b6a8e, "path_get" },
	{ 0x973873ab, "_spin_lock" },
	{ 0xa4709493, "per_cpu__current_task" },
	{ 0x268cc6a2, "sys_close" },
	{ 0xa7fd7f47, "filp_open" },
	{ 0xc58cdb60, "lookup_address" },
	{ 0xb72397d5, "printk" },
	{ 0x12210490, "pv_mmu_ops" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";

