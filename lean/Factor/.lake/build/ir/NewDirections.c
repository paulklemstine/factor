// Lean compiler output
// Module: NewDirections
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
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__6___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
static lean_object* lp_RequestProject_fib__local___closed__1;
static lean_object* lp_RequestProject_cf__step__mat___closed__4;
LEAN_EXPORT lean_object* lp_RequestProject_fib__local___boxed(lean_object*);
lean_object* l_Fin_cases___redArg(lean_object*, lean_object*, lean_object*);
static lean_object* lp_RequestProject_cf__step__mat___closed__6;
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__2___boxed(lean_object*, lean_object*, lean_object*);
static lean_object* lp_RequestProject_cf__step__mat___closed__5;
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__3___boxed(lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_to_int(lean_object*);
lean_object* l_Int_pow(lean_object*, lean_object*);
static lean_object* lp_RequestProject_cf__step__mat___closed__1;
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__1___boxed(lean_object*, lean_object*);
static lean_object* lp_RequestProject_norm__sqrt2___closed__0;
static lean_object* lp_RequestProject_cf__step__mat___closed__0;
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat(lean_object*, lean_object*, lean_object*);
lean_object* lean_int_sub(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_RequestProject_cassini__identity___nativeDecide__1__1;
LEAN_EXPORT lean_object* lp_RequestProject_fib__local(lean_object*);
lean_object* lean_int_mul(lean_object*, lean_object*);
static lean_object* lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__2;
static lean_object* lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__0;
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
static lean_object* lp_RequestProject_fib__local___closed__0;
static lean_object* lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__3;
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__6(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_norm__sqrt2(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__0(lean_object*);
static uint8_t lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__6;
static lean_object* lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__4;
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__3(lean_object*, lean_object*, lean_object*);
static lean_object* lp_RequestProject_cf__step__mat___closed__3;
lean_object* lean_int_add(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__2(lean_object*, lean_object*, lean_object*);
lean_object* lp_mathlib_Equiv_refl(lean_object*);
static lean_object* lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__5;
static lean_object* lp_RequestProject_cf__step__mat___closed__2;
uint8_t lean_int_dec_eq(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__1(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_norm__sqrt2___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__0___boxed(lean_object*);
static lean_object* lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__1;
static lean_object* _init_lp_RequestProject_fib__local___closed__0() {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_RequestProject_fib__local___closed__1() {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(1u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_fib__local(lean_object* x_1) {
_start:
{
lean_object* x_2; uint8_t x_3; 
x_2 = lean_unsigned_to_nat(0u);
x_3 = lean_nat_dec_eq(x_1, x_2);
if (x_3 == 1)
{
lean_object* x_4; 
x_4 = lp_RequestProject_fib__local___closed__0;
return x_4;
}
else
{
lean_object* x_5; lean_object* x_6; uint8_t x_7; 
x_5 = lean_unsigned_to_nat(1u);
x_6 = lean_nat_sub(x_1, x_5);
x_7 = lean_nat_dec_eq(x_6, x_2);
if (x_7 == 1)
{
lean_object* x_8; 
lean_dec(x_6);
x_8 = lp_RequestProject_fib__local___closed__1;
return x_8;
}
else
{
lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; 
x_9 = lean_nat_sub(x_6, x_5);
lean_dec(x_6);
x_10 = lean_nat_add(x_9, x_5);
x_11 = lp_RequestProject_fib__local(x_10);
lean_dec(x_10);
x_12 = lp_RequestProject_fib__local(x_9);
lean_dec(x_9);
x_13 = lean_int_add(x_11, x_12);
lean_dec(x_12);
lean_dec(x_11);
return x_13;
}
}
}
}
LEAN_EXPORT lean_object* lp_RequestProject_fib__local___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_RequestProject_fib__local(x_1);
lean_dec(x_1);
return x_2;
}
}
static lean_object* _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__0() {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(1u);
x_2 = lp_RequestProject_fib__local(x_1);
return x_2;
}
}
static lean_object* _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__1() {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__0;
x_2 = lean_int_mul(x_1, x_1);
return x_2;
}
}
static lean_object* _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__2() {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(2u);
x_2 = lp_RequestProject_fib__local(x_1);
return x_2;
}
}
static lean_object* _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__3() {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lp_RequestProject_fib__local(x_1);
return x_2;
}
}
static lean_object* _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__4() {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__3;
x_2 = lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__2;
x_3 = lean_int_mul(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__5() {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__4;
x_2 = lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__1;
x_3 = lean_int_sub(x_2, x_1);
return x_3;
}
}
static uint8_t _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__6() {
_start:
{
lean_object* x_1; lean_object* x_2; uint8_t x_3; 
x_1 = lp_RequestProject_fib__local___closed__1;
x_2 = lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__5;
x_3 = lean_int_dec_eq(x_2, x_1);
return x_3;
}
}
static uint8_t _init_lp_RequestProject_cassini__identity___nativeDecide__1__1() {
_start:
{
uint8_t x_1; 
x_1 = lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__6;
return x_1;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__0(lean_object* x_1) {
_start:
{
lean_internal_panic_unreachable();
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__0___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_RequestProject_cf__step__mat___lam__0(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__1(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_internal_panic_unreachable();
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__1___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_RequestProject_cf__step__mat___lam__1(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__2(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = l_Fin_cases___redArg(x_1, x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__2___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_RequestProject_cf__step__mat___lam__2(x_1, x_2, x_3);
lean_dec(x_3);
lean_dec(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__3(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = l_Fin_cases___redArg(x_1, x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__3___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_RequestProject_cf__step__mat___lam__3(x_1, x_2, x_3);
lean_dec(x_3);
lean_dec(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__6(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; lean_object* x_6; 
x_5 = l_Fin_cases___redArg(x_1, x_2, x_3);
x_6 = lean_apply_1(x_5, x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat___lam__6___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_RequestProject_cf__step__mat___lam__6(x_1, x_2, x_3, x_4);
lean_dec(x_3);
lean_dec_ref(x_1);
return x_5;
}
}
static lean_object* _init_lp_RequestProject_cf__step__mat___closed__0() {
_start:
{
lean_object* x_1; 
x_1 = lp_mathlib_Equiv_refl(lean_box(0));
return x_1;
}
}
static lean_object* _init_lp_RequestProject_cf__step__mat___closed__1() {
_start:
{
lean_object* x_1; 
x_1 = lean_alloc_closure((void*)(lp_RequestProject_cf__step__mat___lam__0___boxed), 1, 0);
return x_1;
}
}
static lean_object* _init_lp_RequestProject_cf__step__mat___closed__2() {
_start:
{
lean_object* x_1; 
x_1 = lean_alloc_closure((void*)(lp_RequestProject_cf__step__mat___lam__1___boxed), 2, 0);
return x_1;
}
}
static lean_object* _init_lp_RequestProject_cf__step__mat___closed__3() {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lp_RequestProject_cf__step__mat___closed__1;
x_2 = lp_RequestProject_fib__local___closed__1;
x_3 = lean_alloc_closure((void*)(lp_RequestProject_cf__step__mat___lam__2___boxed), 3, 2);
lean_closure_set(x_3, 0, x_2);
lean_closure_set(x_3, 1, x_1);
return x_3;
}
}
static lean_object* _init_lp_RequestProject_cf__step__mat___closed__4() {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lp_RequestProject_cf__step__mat___closed__1;
x_2 = lp_RequestProject_fib__local___closed__0;
x_3 = lean_alloc_closure((void*)(lp_RequestProject_cf__step__mat___lam__2___boxed), 3, 2);
lean_closure_set(x_3, 0, x_2);
lean_closure_set(x_3, 1, x_1);
return x_3;
}
}
static lean_object* _init_lp_RequestProject_cf__step__mat___closed__5() {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lp_RequestProject_cf__step__mat___closed__4;
x_2 = lp_RequestProject_fib__local___closed__1;
x_3 = lean_alloc_closure((void*)(lp_RequestProject_cf__step__mat___lam__2___boxed), 3, 2);
lean_closure_set(x_3, 0, x_2);
lean_closure_set(x_3, 1, x_1);
return x_3;
}
}
static lean_object* _init_lp_RequestProject_cf__step__mat___closed__6() {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lp_RequestProject_cf__step__mat___closed__2;
x_2 = lp_RequestProject_cf__step__mat___closed__5;
x_3 = lean_alloc_closure((void*)(lp_RequestProject_cf__step__mat___lam__6___boxed), 4, 2);
lean_closure_set(x_3, 0, x_2);
lean_closure_set(x_3, 1, x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_cf__step__mat(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_4 = lp_RequestProject_cf__step__mat___closed__0;
x_5 = lean_ctor_get(x_4, 0);
lean_inc(x_5);
x_6 = lp_RequestProject_cf__step__mat___closed__3;
x_7 = lean_alloc_closure((void*)(lp_RequestProject_cf__step__mat___lam__3___boxed), 3, 2);
lean_closure_set(x_7, 0, x_1);
lean_closure_set(x_7, 1, x_6);
x_8 = lp_RequestProject_cf__step__mat___closed__6;
x_9 = lean_alloc_closure((void*)(lp_RequestProject_cf__step__mat___lam__6___boxed), 4, 2);
lean_closure_set(x_9, 0, x_7);
lean_closure_set(x_9, 1, x_8);
x_10 = lean_apply_3(x_5, x_9, x_2, x_3);
return x_10;
}
}
static lean_object* _init_lp_RequestProject_norm__sqrt2___closed__0() {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(2u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_norm__sqrt2(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_3 = lean_unsigned_to_nat(2u);
x_4 = l_Int_pow(x_1, x_3);
x_5 = lp_RequestProject_norm__sqrt2___closed__0;
x_6 = l_Int_pow(x_2, x_3);
x_7 = lean_int_mul(x_5, x_6);
lean_dec(x_6);
x_8 = lean_int_sub(x_4, x_7);
lean_dec(x_7);
lean_dec(x_4);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_norm__sqrt2___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_RequestProject_norm__sqrt2(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
return x_3;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_RequestProject_NewDirections(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
lp_RequestProject_fib__local___closed__0 = _init_lp_RequestProject_fib__local___closed__0();
lean_mark_persistent(lp_RequestProject_fib__local___closed__0);
lp_RequestProject_fib__local___closed__1 = _init_lp_RequestProject_fib__local___closed__1();
lean_mark_persistent(lp_RequestProject_fib__local___closed__1);
lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__0 = _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__0();
lean_mark_persistent(lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__0);
lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__1 = _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__1();
lean_mark_persistent(lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__1);
lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__2 = _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__2();
lean_mark_persistent(lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__2);
lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__3 = _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__3();
lean_mark_persistent(lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__3);
lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__4 = _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__4();
lean_mark_persistent(lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__4);
lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__5 = _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__5();
lean_mark_persistent(lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__5);
lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__6 = _init_lp_RequestProject_cassini__identity___nativeDecide__1__1___closed__6();
lp_RequestProject_cassini__identity___nativeDecide__1__1 = _init_lp_RequestProject_cassini__identity___nativeDecide__1__1();
lp_RequestProject_cf__step__mat___closed__0 = _init_lp_RequestProject_cf__step__mat___closed__0();
lean_mark_persistent(lp_RequestProject_cf__step__mat___closed__0);
lp_RequestProject_cf__step__mat___closed__1 = _init_lp_RequestProject_cf__step__mat___closed__1();
lean_mark_persistent(lp_RequestProject_cf__step__mat___closed__1);
lp_RequestProject_cf__step__mat___closed__2 = _init_lp_RequestProject_cf__step__mat___closed__2();
lean_mark_persistent(lp_RequestProject_cf__step__mat___closed__2);
lp_RequestProject_cf__step__mat___closed__3 = _init_lp_RequestProject_cf__step__mat___closed__3();
lean_mark_persistent(lp_RequestProject_cf__step__mat___closed__3);
lp_RequestProject_cf__step__mat___closed__4 = _init_lp_RequestProject_cf__step__mat___closed__4();
lean_mark_persistent(lp_RequestProject_cf__step__mat___closed__4);
lp_RequestProject_cf__step__mat___closed__5 = _init_lp_RequestProject_cf__step__mat___closed__5();
lean_mark_persistent(lp_RequestProject_cf__step__mat___closed__5);
lp_RequestProject_cf__step__mat___closed__6 = _init_lp_RequestProject_cf__step__mat___closed__6();
lean_mark_persistent(lp_RequestProject_cf__step__mat___closed__6);
lp_RequestProject_norm__sqrt2___closed__0 = _init_lp_RequestProject_norm__sqrt2___closed__0();
lean_mark_persistent(lp_RequestProject_norm__sqrt2___closed__0);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
