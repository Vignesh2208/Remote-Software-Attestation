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
	{ 0x2bc801eb, "remove_proc_entry" },
	{ 0x9629486a, "per_cpu__cpu_number" },
	{ 0xb72397d5, "printk" },
	{ 0xacdeb154, "__tracepoint_module_get" },
	{ 0x2da418b5, "copy_to_user" },
	{ 0xabde244e, "module_put" },
	{ 0xafdd7304, "init_task" },
	{ 0xf0fdf6cb, "__stack_chk_fail" },
	{ 0x20a4158e, "crypto_destroy_tfm" },
	{ 0x714242a0, "create_proc_entry" },
	{ 0x280f9f14, "__per_cpu_offset" },
	{ 0x5c265cba, "sg_init_one" },
	{ 0xb742fd7, "simple_strtol" },
	{ 0x5cb564a9, "crypto_alloc_base" },
	{ 0xf2a644fb, "copy_from_user" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";

