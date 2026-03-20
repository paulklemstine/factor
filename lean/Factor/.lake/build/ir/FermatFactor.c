// Lean compiler output
// Module: FermatFactor
// Imports: public import Init public import Mathlib public import BerggrenTree
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
lean_object* lean_nat_gcd(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_searchBerggrenTree(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject___private_FermatFactor_0__instReprTreePath_repr_match__1_splitter___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_div(lean_object*, lean_object*);
lean_object* lp_batteries_Nat_sqrt(lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_berggrenFermatFactor(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_fermatSearch(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_berggrenFermatFactor___boxed(lean_object*, lean_object*);
lean_object* l_List_appendTR___redArg(lean_object*, lean_object*);
lean_object* lp_RequestProject_berggrenTripleAux(lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_searchBerggrenTree___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject___private_FermatFactor_0__instReprTreePath_repr_match__1_splitter(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_abs(lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
lean_object* lean_nat_mul(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_fermatSearch___boxed(lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_RequestProject_fermatSearch(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; uint8_t x_5; 
x_4 = lean_unsigned_to_nat(0u);
x_5 = lean_nat_dec_eq(x_3, x_4);
if (x_5 == 1)
{
lean_object* x_6; 
lean_dec(x_3);
lean_dec(x_2);
x_6 = lean_box(0);
return x_6;
}
else
{
lean_object* x_7; uint8_t x_8; 
x_7 = lean_nat_mul(x_2, x_2);
x_8 = lean_nat_dec_lt(x_7, x_1);
if (x_8 == 0)
{
lean_object* x_9; lean_object* x_10; lean_object* x_11; uint8_t x_12; 
x_9 = lean_nat_sub(x_7, x_1);
lean_dec(x_7);
x_10 = lp_batteries_Nat_sqrt(x_9);
x_11 = lean_nat_mul(x_10, x_10);
x_12 = lean_nat_dec_eq(x_11, x_9);
lean_dec(x_9);
lean_dec(x_11);
if (x_12 == 0)
{
lean_object* x_13; lean_object* x_14; lean_object* x_15; 
lean_dec(x_10);
x_13 = lean_unsigned_to_nat(1u);
x_14 = lean_nat_sub(x_3, x_13);
lean_dec(x_3);
x_15 = lean_nat_add(x_2, x_13);
lean_dec(x_2);
x_2 = x_15;
x_3 = x_14;
goto _start;
}
else
{
lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; 
lean_dec(x_3);
x_17 = lean_nat_sub(x_2, x_10);
x_18 = lean_nat_add(x_2, x_10);
lean_dec(x_10);
lean_dec(x_2);
x_19 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_19, 0, x_17);
lean_ctor_set(x_19, 1, x_18);
x_20 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_20, 0, x_19);
return x_20;
}
}
else
{
lean_object* x_21; 
lean_dec(x_7);
lean_dec(x_3);
lean_dec(x_2);
x_21 = lean_box(0);
return x_21;
}
}
}
}
LEAN_EXPORT lean_object* lp_RequestProject_fermatSearch___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_RequestProject_fermatSearch(x_1, x_2, x_3);
lean_dec(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_searchBerggrenTree(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; uint8_t x_5; 
x_4 = lean_unsigned_to_nat(0u);
x_5 = lean_nat_dec_eq(x_3, x_4);
if (x_5 == 1)
{
lean_object* x_6; 
lean_dec(x_2);
x_6 = lean_box(0);
return x_6;
}
else
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; uint8_t x_36; uint8_t x_42; lean_object* x_43; lean_object* x_53; uint8_t x_54; uint8_t x_60; uint8_t x_61; lean_object* x_62; uint8_t x_64; 
x_7 = lp_RequestProject_berggrenTripleAux(x_2);
x_8 = lean_ctor_get(x_7, 1);
lean_inc(x_8);
x_9 = lean_ctor_get(x_7, 0);
lean_inc(x_9);
if (lean_is_exclusive(x_7)) {
 lean_ctor_release(x_7, 0);
 lean_ctor_release(x_7, 1);
 x_10 = x_7;
} else {
 lean_dec_ref(x_7);
 x_10 = lean_box(0);
}
x_11 = lean_ctor_get(x_8, 0);
lean_inc(x_11);
x_12 = lean_ctor_get(x_8, 1);
lean_inc(x_12);
if (lean_is_exclusive(x_8)) {
 lean_ctor_release(x_8, 0);
 lean_ctor_release(x_8, 1);
 x_13 = x_8;
} else {
 lean_dec_ref(x_8);
 x_13 = lean_box(0);
}
x_14 = lean_unsigned_to_nat(1u);
x_15 = lean_nat_sub(x_3, x_14);
x_27 = lean_nat_abs(x_9);
lean_dec(x_9);
x_28 = lean_nat_abs(x_11);
lean_dec(x_11);
x_29 = lean_nat_gcd(x_27, x_1);
lean_dec(x_27);
x_30 = lean_nat_gcd(x_28, x_1);
lean_dec(x_28);
x_31 = lean_box(0);
x_42 = lean_nat_dec_lt(x_30, x_1);
x_60 = lean_nat_dec_lt(x_14, x_29);
x_61 = lean_nat_dec_lt(x_14, x_30);
if (x_60 == 0)
{
x_64 = x_60;
goto block_69;
}
else
{
uint8_t x_70; 
x_70 = lean_nat_dec_lt(x_29, x_1);
x_64 = x_70;
goto block_69;
}
block_26:
{
lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
lean_inc(x_2);
x_17 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_17, 0, x_2);
x_18 = lp_RequestProject_searchBerggrenTree(x_1, x_17, x_15);
x_19 = l_List_appendTR___redArg(x_16, x_18);
lean_inc(x_2);
x_20 = lean_alloc_ctor(2, 1, 0);
lean_ctor_set(x_20, 0, x_2);
x_21 = lp_RequestProject_searchBerggrenTree(x_1, x_20, x_15);
x_22 = l_List_appendTR___redArg(x_19, x_21);
x_23 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_23, 0, x_2);
x_24 = lp_RequestProject_searchBerggrenTree(x_1, x_23, x_15);
lean_dec(x_15);
x_25 = l_List_appendTR___redArg(x_22, x_24);
return x_25;
}
block_41:
{
if (x_36 == 0)
{
lean_dec_ref(x_35);
lean_dec(x_34);
lean_dec(x_33);
x_16 = x_32;
goto block_26;
}
else
{
lean_object* x_37; uint8_t x_38; 
x_37 = lean_nat_mul(x_33, x_34);
lean_dec(x_34);
lean_dec(x_33);
x_38 = lean_nat_dec_eq(x_37, x_1);
lean_dec(x_37);
if (x_38 == 0)
{
lean_dec_ref(x_35);
x_16 = x_32;
goto block_26;
}
else
{
lean_object* x_39; lean_object* x_40; 
x_39 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_39, 0, x_35);
lean_ctor_set(x_39, 1, x_31);
x_40 = l_List_appendTR___redArg(x_32, x_39);
x_16 = x_40;
goto block_26;
}
}
}
block_52:
{
lean_object* x_44; lean_object* x_45; lean_object* x_46; 
x_44 = lean_nat_abs(x_12);
lean_dec(x_12);
x_45 = lean_unsigned_to_nat(100u);
x_46 = lp_RequestProject_fermatSearch(x_1, x_44, x_45);
if (lean_obj_tag(x_46) == 0)
{
x_16 = x_43;
goto block_26;
}
else
{
lean_object* x_47; lean_object* x_48; lean_object* x_49; uint8_t x_50; 
x_47 = lean_ctor_get(x_46, 0);
lean_inc(x_47);
lean_dec_ref(x_46);
x_48 = lean_ctor_get(x_47, 0);
lean_inc(x_48);
x_49 = lean_ctor_get(x_47, 1);
lean_inc(x_49);
x_50 = lean_nat_dec_lt(x_14, x_48);
if (x_50 == 0)
{
x_32 = x_43;
x_33 = x_48;
x_34 = x_49;
x_35 = x_47;
x_36 = x_50;
goto block_41;
}
else
{
uint8_t x_51; 
x_51 = lean_nat_dec_lt(x_14, x_49);
x_32 = x_43;
x_33 = x_48;
x_34 = x_49;
x_35 = x_47;
x_36 = x_51;
goto block_41;
}
}
}
block_59:
{
if (x_54 == 0)
{
lean_dec(x_30);
lean_dec(x_13);
x_43 = x_53;
goto block_52;
}
else
{
lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; 
x_55 = lean_nat_div(x_1, x_30);
if (lean_is_scalar(x_13)) {
 x_56 = lean_alloc_ctor(0, 2, 0);
} else {
 x_56 = x_13;
}
lean_ctor_set(x_56, 0, x_30);
lean_ctor_set(x_56, 1, x_55);
x_57 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_57, 0, x_56);
lean_ctor_set(x_57, 1, x_31);
x_58 = l_List_appendTR___redArg(x_53, x_57);
x_43 = x_58;
goto block_52;
}
}
block_63:
{
if (x_61 == 0)
{
x_53 = x_62;
x_54 = x_61;
goto block_59;
}
else
{
x_53 = x_62;
x_54 = x_42;
goto block_59;
}
}
block_69:
{
if (x_64 == 0)
{
lean_dec(x_29);
lean_dec(x_10);
x_62 = x_31;
goto block_63;
}
else
{
lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; 
x_65 = lean_nat_div(x_1, x_29);
if (lean_is_scalar(x_10)) {
 x_66 = lean_alloc_ctor(0, 2, 0);
} else {
 x_66 = x_10;
}
lean_ctor_set(x_66, 0, x_29);
lean_ctor_set(x_66, 1, x_65);
x_67 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_67, 0, x_66);
lean_ctor_set(x_67, 1, x_31);
x_68 = l_List_appendTR___redArg(x_31, x_67);
x_62 = x_68;
goto block_63;
}
}
}
}
}
LEAN_EXPORT lean_object* lp_RequestProject_searchBerggrenTree___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_RequestProject_searchBerggrenTree(x_1, x_2, x_3);
lean_dec(x_3);
lean_dec(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_berggrenFermatFactor(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; 
x_3 = lean_box(0);
x_4 = lp_RequestProject_searchBerggrenTree(x_1, x_3, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_RequestProject_berggrenFermatFactor___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_RequestProject_berggrenFermatFactor(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_RequestProject___private_FermatFactor_0__instReprTreePath_repr_match__1_splitter___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
switch (lean_obj_tag(x_1)) {
case 0:
{
lean_object* x_6; lean_object* x_7; 
lean_dec(x_5);
lean_dec(x_4);
lean_dec(x_3);
x_6 = lean_box(0);
x_7 = lean_apply_1(x_2, x_6);
return x_7;
}
case 1:
{
lean_object* x_8; lean_object* x_9; 
lean_dec(x_5);
lean_dec(x_4);
lean_dec(x_2);
x_8 = lean_ctor_get(x_1, 0);
lean_inc(x_8);
lean_dec_ref(x_1);
x_9 = lean_apply_1(x_3, x_8);
return x_9;
}
case 2:
{
lean_object* x_10; lean_object* x_11; 
lean_dec(x_5);
lean_dec(x_3);
lean_dec(x_2);
x_10 = lean_ctor_get(x_1, 0);
lean_inc(x_10);
lean_dec_ref(x_1);
x_11 = lean_apply_1(x_4, x_10);
return x_11;
}
default: 
{
lean_object* x_12; lean_object* x_13; 
lean_dec(x_4);
lean_dec(x_3);
lean_dec(x_2);
x_12 = lean_ctor_get(x_1, 0);
lean_inc(x_12);
lean_dec_ref(x_1);
x_13 = lean_apply_1(x_5, x_12);
return x_13;
}
}
}
}
LEAN_EXPORT lean_object* lp_RequestProject___private_FermatFactor_0__instReprTreePath_repr_match__1_splitter(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_RequestProject___private_FermatFactor_0__instReprTreePath_repr_match__1_splitter___redArg(x_2, x_3, x_4, x_5, x_6);
return x_7;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib(uint8_t builtin);
lean_object* initialize_RequestProject_BerggrenTree(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_RequestProject_FermatFactor(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_RequestProject_BerggrenTree(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
