// Lean compiler output
// Module: QuantumCompression
// Imports: public import Init public import Mathlib
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
lean_object* l_List_lengthTR___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_trivial__codebook___lam__0___boxed(lean_object*);
static lean_object* lp_RequestProject_trivial__codebook___closed__0;
static lean_object* lp_RequestProject_trivial__codebook___closed__1;
LEAN_EXPORT lean_object* lp_RequestProject_Codebook_comp___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_circuit__length(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_circuit__length___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_trivial__codebook___lam__0(lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_circuit__length___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_trivial__codebook(lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_Codebook_comp___redArg___lam__1(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_Codebook_comp(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_Codebook_comp___redArg___lam__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_circuit__length___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_trivial__codebook___lam__0(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_trivial__codebook___lam__0___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_RequestProject_trivial__codebook___lam__0(x_1);
lean_dec(x_1);
return x_2;
}
}
static lean_object* _init_lp_RequestProject_trivial__codebook___closed__0() {
_start:
{
lean_object* x_1; 
x_1 = lean_alloc_closure((void*)(lp_RequestProject_trivial__codebook___lam__0___boxed), 1, 0);
return x_1;
}
}
static lean_object* _init_lp_RequestProject_trivial__codebook___closed__1() {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lp_RequestProject_trivial__codebook___closed__0;
x_2 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_2, 0, x_1);
lean_ctor_set(x_2, 1, x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_trivial__codebook(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_RequestProject_trivial__codebook___closed__1;
return x_2;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_Codebook_comp___redArg___lam__0(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; 
x_4 = lean_apply_1(x_1, x_3);
x_5 = lean_apply_1(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_Codebook_comp___redArg___lam__1(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; 
x_4 = lean_apply_1(x_1, x_3);
x_5 = lean_apply_1(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_Codebook_comp___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; uint8_t x_5; 
x_3 = lean_ctor_get(x_2, 0);
lean_inc(x_3);
x_4 = lean_ctor_get(x_2, 1);
lean_inc(x_4);
lean_dec_ref(x_2);
x_5 = !lean_is_exclusive(x_1);
if (x_5 == 0)
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; 
x_6 = lean_ctor_get(x_1, 0);
x_7 = lean_ctor_get(x_1, 1);
x_8 = lean_alloc_closure((void*)(lp_RequestProject_Codebook_comp___redArg___lam__0), 3, 2);
lean_closure_set(x_8, 0, x_4);
lean_closure_set(x_8, 1, x_7);
x_9 = lean_alloc_closure((void*)(lp_RequestProject_Codebook_comp___redArg___lam__1), 3, 2);
lean_closure_set(x_9, 0, x_6);
lean_closure_set(x_9, 1, x_3);
lean_ctor_set(x_1, 1, x_8);
lean_ctor_set(x_1, 0, x_9);
return x_1;
}
else
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; 
x_10 = lean_ctor_get(x_1, 0);
x_11 = lean_ctor_get(x_1, 1);
lean_inc(x_11);
lean_inc(x_10);
lean_dec(x_1);
x_12 = lean_alloc_closure((void*)(lp_RequestProject_Codebook_comp___redArg___lam__0), 3, 2);
lean_closure_set(x_12, 0, x_4);
lean_closure_set(x_12, 1, x_11);
x_13 = lean_alloc_closure((void*)(lp_RequestProject_Codebook_comp___redArg___lam__1), 3, 2);
lean_closure_set(x_13, 0, x_10);
lean_closure_set(x_13, 1, x_3);
x_14 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_14, 0, x_13);
lean_ctor_set(x_14, 1, x_12);
return x_14;
}
}
}
LEAN_EXPORT lean_object* lp_RequestProject_Codebook_comp(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_RequestProject_Codebook_comp___redArg(x_4, x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_circuit__length___redArg(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = l_List_lengthTR___redArg(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_circuit__length___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_RequestProject_circuit__length___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_circuit__length(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = l_List_lengthTR___redArg(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_circuit__length___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_RequestProject_circuit__length(x_1, x_2);
lean_dec(x_2);
return x_3;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_RequestProject_QuantumCompression(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
lp_RequestProject_trivial__codebook___closed__0 = _init_lp_RequestProject_trivial__codebook___closed__0();
lean_mark_persistent(lp_RequestProject_trivial__codebook___closed__0);
lp_RequestProject_trivial__codebook___closed__1 = _init_lp_RequestProject_trivial__codebook___closed__1();
lean_mark_persistent(lp_RequestProject_trivial__codebook___closed__1);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
