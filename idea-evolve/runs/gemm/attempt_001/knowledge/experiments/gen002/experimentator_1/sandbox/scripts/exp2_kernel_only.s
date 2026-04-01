	.file	"exp2_kernel_only.cpp"
# GNU C++17 (Ubuntu 13.3.0-6ubuntu2~24.04.1) version 13.3.0 (x86_64-linux-gnu)
#	compiled by GNU C version 13.3.0, GMP version 6.3.0, MPFR version 4.2.1, MPC version 1.3.1, isl version isl-0.26-GMP

# GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
# options passed: -march=tigerlake -mmmx -mpopcnt -msse -msse2 -msse3 -mssse3 -msse4.1 -msse4.2 -mavx -mavx2 -mno-sse4a -mno-fma4 -mno-xop -mfma -mbmi -mbmi2 -maes -mpclmul -mavx512dq -mavx512cd -mno-avx512er -mno-avx512pf -mavx512vbmi -mavx512ifma -mno-avx5124vnniw -mno-avx5124fmaps -mavx512vbmi2 -mgfni -mvpclmulqdq -mno-avx512bf16 -mavx512vp2intersect -mno-3dnow -madx -mabm -mno-cldemote -mclflushopt -mclwb -mno-clzero -mcx16 -mno-enqcmd -mf16c -mfsgsbase -mfxsr -mno-hle -msahf -mno-lwp -mlzcnt -mmovbe -mmovdir64b -mmovdiri -mno-mwaitx -mno-pconfig -mpku -mno-prefetchwt1 -mprfchw -mno-ptwrite -mrdpid -mrdrnd -mrdseed -mno-rtm -mno-serialize -mno-sgx -msha -mshstk -mno-tbm -mno-tsxldtrk -mvaes -mno-waitpkg -mno-wbnoinvd -mxsave -mxsavec -mxsaveopt -mxsaves -mno-amx-tile -mno-amx-int8 -mno-amx-bf16 -mno-uintr -mno-hreset -mno-kl -mno-widekl -mno-avxvnni -mno-avx512fp16 -mno-avxifma -mno-avxvnniint8 -mno-avxneconvert -mno-cmpccxadd -mno-amx-fp16 -mno-prefetchi -mno-raoint -mno-amx-complex --param=l1-cache-size=48 --param=l1-cache-line-size=64 --param=l2-cache-size=8192 -mtune=tigerlake -mavx512f -mavx512bw -mavx512vl -mavx512vpopcntdq -mavx512bitalg -mavx512vnni -O3 -std=c++17 -fasynchronous-unwind-tables -fstack-protector-strong -fstack-clash-protection -fcf-protection
	.text
	.p2align 4
	.globl	_Z17micro_kernel_4x64iPKhS0_Pii
	.type	_Z17micro_kernel_4x64iPKhS0_Pii, @function
_Z17micro_kernel_4x64iPKhS0_Pii:
.LFB6442:
	.cfi_startproc
	endbr64	
	pushq	%rbp	#
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
# scripts/exp2_kernel_only.cpp:18:         acc[r][0] = acc[r][1] = _mm512_setzero_si512();
	vpxor	%xmm0, %xmm0, %xmm0	# tmp332
# scripts/exp2_kernel_only.cpp:15: ) {
	movq	%rcx, %rax	# tmp619, C
	movq	%rsp, %rbp	#,
	.cfi_def_cfa_register 6
	andq	$-64, %rsp	#,
	subq	$576, %rsp	#,
# scripts/exp2_kernel_only.cpp:15: ) {
	movq	%fs:40, %rcx	# MEM[(<address-space-1> long unsigned int *)40B], tmp621
	movq	%rcx, 568(%rsp)	# tmp621, D.39099
	xorl	%ecx, %ecx	# tmp621
# scripts/exp2_kernel_only.cpp:18:         acc[r][0] = acc[r][1] = _mm512_setzero_si512();
	vmovdqa64	%zmm0, 64(%rsp)	# tmp332, acc[0][1]
# scripts/exp2_kernel_only.cpp:18:         acc[r][0] = acc[r][1] = _mm512_setzero_si512();
	vmovdqa64	%zmm0, (%rsp)	# tmp332, acc[0][0]
# scripts/exp2_kernel_only.cpp:18:         acc[r][0] = acc[r][1] = _mm512_setzero_si512();
	vmovdqa64	%zmm0, 192(%rsp)	# tmp332, acc[1][1]
# scripts/exp2_kernel_only.cpp:18:         acc[r][0] = acc[r][1] = _mm512_setzero_si512();
	vmovdqa64	%zmm0, 128(%rsp)	# tmp332, acc[1][0]
# scripts/exp2_kernel_only.cpp:18:         acc[r][0] = acc[r][1] = _mm512_setzero_si512();
	vmovdqa64	%zmm0, 320(%rsp)	# tmp332, acc[2][1]
# scripts/exp2_kernel_only.cpp:18:         acc[r][0] = acc[r][1] = _mm512_setzero_si512();
	vmovdqa64	%zmm0, 256(%rsp)	# tmp332, acc[2][0]
# scripts/exp2_kernel_only.cpp:18:         acc[r][0] = acc[r][1] = _mm512_setzero_si512();
	vmovdqa64	%zmm0, 448(%rsp)	# tmp332, acc[3][1]
# scripts/exp2_kernel_only.cpp:18:         acc[r][0] = acc[r][1] = _mm512_setzero_si512();
	vmovdqa64	%zmm0, 384(%rsp)	# tmp332, acc[3][0]
# scripts/exp2_kernel_only.cpp:21:     for (int k = 0; k < kc; ++k) {
	testl	%edi, %edi	# kc
	jle	.L2	#,
	vmovdqa64	%zmm0, %zmm4	#, acc_I_I_lsm.29
	vmovdqa64	%zmm0, %zmm5	#, acc_I_I_lsm.28
	vmovdqa64	%zmm0, %zmm6	#, acc_I_I_lsm.27
	movslq	%edi, %rdi	# kc, kc
	leaq	-8(,%rdi,8), %rcx	#, tmp611
	leaq	(%rsi,%rdi,8), %r9	#, _245
	vmovdqa64	%zmm0, %zmm7	#, acc_I_I_lsm.26
	vmovdqa64	%zmm0, %zmm8	#, acc_I_I_lsm.25
	shrq	$3, %rcx	#, tmp609
	vmovdqa64	%zmm0, %zmm9	#, acc_I_I_lsm.24
	vmovdqa64	%zmm0, %zmm10	#, acc_I_I_lsm.23
	incq	%rcx	# tmp612
	vmovdqa64	%zmm0, %zmm11	#, acc_I_I_lsm.22
	andl	$3, %ecx	#, tmp613
	je	.L3	#,
	cmpq	$1, %rcx	#, tmp613
	je	.L15	#,
	cmpq	$2, %rcx	#, tmp613
	je	.L16	#,
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	(%rsi), %zmm1	# MEM[(const uint8_t *)_280], tmp343
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6501:   return *(__m512i_u *)__P;
	vmovdqu64	(%rdx), %zmm12	# MEM[(__m512i_u * {ref-all})_62], MEM[(__m512i_u * {ref-all})_62]
# scripts/exp2_kernel_only.cpp:21:     for (int k = 0; k < kc; ++k) {
	addq	$8, %rsi	#, ivtmp.36
	addq	$64, %rdx	#, ivtmp.35
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-7(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 1B], tmp344
	vpbroadcastb	-3(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 5B], tmp412
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp343, tmp345
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-1(%rsi), %zmm17	# MEM[(const uint8_t *)_280 + 7B], tmp446
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp345
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp352
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-5(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 3B], tmp378
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp352, tmp357
	vpopcntb	%zmm0, %zmm0	# tmp345, tmp350
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp357, tmp350, _135
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-6(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 2B], tmp377
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpmovsxbw	%ymm0, %zmm11	# tmp359, acc_I_I_lsm.22
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _135, tmp368
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpmovsxbw	%ymm0, %zmm10	# tmp368, acc_I_I_lsm.23
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp377, tmp379
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp386
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp386, tmp391
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp379
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp379, tmp384
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp391, tmp384, _180
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-4(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 4B], tmp411
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpmovsxbw	%ymm0, %zmm9	# tmp393, acc_I_I_lsm.24
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _180, tmp402
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpmovsxbw	%ymm0, %zmm8	# tmp402, acc_I_I_lsm.25
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp411, tmp413
	vpternlogq	$228, %zmm12, %zmm14, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp420
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp420, tmp425
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm14, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp413
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-2(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 6B], tmp445
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp413, tmp418
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp425, tmp418, _225
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm14, %zmm1	# tmp445, tmp447
	vpternlogq	$228, %zmm12, %zmm17, %zmm14	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp454
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm14, %zmm14	# tmp454, tmp459
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm17, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp447
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpmovsxbw	%ymm0, %zmm7	# tmp427, acc_I_I_lsm.26
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _225, tmp436
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp447, tmp452
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpmovsxbw	%ymm0, %zmm6	# tmp436, acc_I_I_lsm.27
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm14, %zmm1, %zmm1	# tmp459, tmp452, _270
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpmovsxbw	%ymm1, %zmm5	# tmp461, acc_I_I_lsm.28
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm1, %ymm1	# _270, tmp470
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpmovsxbw	%ymm1, %zmm4	# tmp470, acc_I_I_lsm.29
.L16:
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	(%rsi), %zmm1	# MEM[(const uint8_t *)_280], tmp343
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6501:   return *(__m512i_u *)__P;
	vmovdqu64	(%rdx), %zmm12	# MEM[(__m512i_u * {ref-all})_62], MEM[(__m512i_u * {ref-all})_62]
# scripts/exp2_kernel_only.cpp:21:     for (int k = 0; k < kc; ++k) {
	addq	$8, %rsi	#, ivtmp.36
	addq	$64, %rdx	#, ivtmp.35
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-7(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 1B], tmp344
	vpbroadcastb	-3(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 5B], tmp412
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp343, tmp345
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-1(%rsi), %zmm17	# MEM[(const uint8_t *)_280 + 7B], tmp446
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp345
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp352
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-5(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 3B], tmp378
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp352, tmp357
	vpopcntb	%zmm0, %zmm0	# tmp345, tmp350
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp357, tmp350, _135
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-6(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 2B], tmp377
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm13	# tmp359, tmp363
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _135, tmp368
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp368, tmp372
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm11, %zmm13, %zmm11	# acc_I_I_lsm.22, tmp363, acc_I_I_lsm.22
	vpaddw	%zmm10, %zmm0, %zmm10	# acc_I_I_lsm.23, tmp372, acc_I_I_lsm.23
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp377, tmp379
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp386
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp386, tmp391
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp379
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp379, tmp384
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp391, tmp384, _180
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-4(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 4B], tmp411
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm15	# tmp393, tmp397
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _180, tmp402
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp402, tmp406
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm9, %zmm15, %zmm9	# acc_I_I_lsm.24, tmp397, acc_I_I_lsm.24
	vpaddw	%zmm8, %zmm0, %zmm8	# acc_I_I_lsm.25, tmp406, acc_I_I_lsm.25
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp411, tmp413
	vpternlogq	$228, %zmm12, %zmm14, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp420
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp420, tmp425
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm14, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp413
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-2(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 6B], tmp445
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp413, tmp418
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp425, tmp418, _225
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm1	# tmp427, tmp431
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _225, tmp436
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm7, %zmm1, %zmm7	# acc_I_I_lsm.26, tmp431, acc_I_I_lsm.26
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm14, %zmm1	# tmp445, tmp447
	vpternlogq	$228, %zmm12, %zmm17, %zmm14	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp454
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm14, %zmm14	# tmp454, tmp459
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm17, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp447
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp436, tmp440
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp447, tmp452
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm6, %zmm0, %zmm6	# acc_I_I_lsm.27, tmp440, acc_I_I_lsm.27
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm14, %zmm1, %zmm1	# tmp459, tmp452, _270
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm12	# tmp461, tmp465
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm1, %ymm1	# _270, tmp470
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm1	# tmp470, tmp474
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm5, %zmm12, %zmm5	# acc_I_I_lsm.28, tmp465, acc_I_I_lsm.28
	vpaddw	%zmm4, %zmm1, %zmm4	# acc_I_I_lsm.29, tmp474, acc_I_I_lsm.29
.L15:
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	(%rsi), %zmm1	# MEM[(const uint8_t *)_280], tmp343
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6501:   return *(__m512i_u *)__P;
	vmovdqu64	(%rdx), %zmm12	# MEM[(__m512i_u * {ref-all})_62], MEM[(__m512i_u * {ref-all})_62]
# scripts/exp2_kernel_only.cpp:21:     for (int k = 0; k < kc; ++k) {
	addq	$8, %rsi	#, ivtmp.36
	addq	$64, %rdx	#, ivtmp.35
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-7(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 1B], tmp344
	vpbroadcastb	-3(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 5B], tmp412
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp343, tmp345
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-1(%rsi), %zmm17	# MEM[(const uint8_t *)_280 + 7B], tmp446
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp345
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp352
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-5(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 3B], tmp378
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp352, tmp357
	vpopcntb	%zmm0, %zmm0	# tmp345, tmp350
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp357, tmp350, _135
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-6(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 2B], tmp377
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm13	# tmp359, tmp363
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _135, tmp368
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp368, tmp372
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm11, %zmm13, %zmm13	# acc_I_I_lsm.22, tmp363, tmp367
	vpaddw	%zmm10, %zmm0, %zmm3	# acc_I_I_lsm.23, tmp372, tmp376
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp377, tmp379
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp386
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp386, tmp391
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp379
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm13, %zmm11	# tmp367, acc_I_I_lsm.22
	vmovdqa64	%zmm3, %zmm10	# tmp376, acc_I_I_lsm.23
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp379, tmp384
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp391, tmp384, _180
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-4(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 4B], tmp411
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm15	# tmp393, tmp397
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _180, tmp402
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp402, tmp406
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm9, %zmm15, %zmm15	# acc_I_I_lsm.24, tmp397, tmp401
	vpaddw	%zmm8, %zmm0, %zmm2	# acc_I_I_lsm.25, tmp406, tmp410
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp411, tmp413
	vpternlogq	$228, %zmm12, %zmm14, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp420
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp420, tmp425
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm14, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp413
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	-2(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 6B], tmp445
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm15, %zmm9	# tmp401, acc_I_I_lsm.24
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp413, tmp418
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm2, %zmm8	# tmp410, acc_I_I_lsm.25
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp425, tmp418, _225
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm1	# tmp427, tmp431
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _225, tmp436
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm7, %zmm1, %zmm16	# acc_I_I_lsm.26, tmp431, tmp435
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm14, %zmm1	# tmp445, tmp447
	vpternlogq	$228, %zmm12, %zmm17, %zmm14	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp454
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm14, %zmm14	# tmp454, tmp459
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm17, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp447
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp436, tmp440
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm16, %zmm7	# tmp435, acc_I_I_lsm.26
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp447, tmp452
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm6, %zmm0, %zmm0	# acc_I_I_lsm.27, tmp440, tmp444
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm0, %zmm6	# tmp444, acc_I_I_lsm.27
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm14, %zmm1, %zmm1	# tmp459, tmp452, _270
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm12	# tmp461, tmp465
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm1, %ymm1	# _270, tmp470
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm1	# tmp470, tmp474
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm5, %zmm12, %zmm12	# acc_I_I_lsm.28, tmp465, tmp469
	vpaddw	%zmm4, %zmm1, %zmm1	# acc_I_I_lsm.29, tmp474, tmp478
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm12, %zmm5	# tmp469, acc_I_I_lsm.28
	vmovdqa64	%zmm1, %zmm4	# tmp478, acc_I_I_lsm.29
# scripts/exp2_kernel_only.cpp:21:     for (int k = 0; k < kc; ++k) {
	cmpq	%rsi, %r9	# ivtmp.36, _245
	je	.L21	#,
.L3:
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	(%rsi), %zmm1	# MEM[(const uint8_t *)_280], tmp343
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6501:   return *(__m512i_u *)__P;
	vmovdqu64	(%rdx), %zmm12	# MEM[(__m512i_u * {ref-all})_62], MEM[(__m512i_u * {ref-all})_62]
# scripts/exp2_kernel_only.cpp:21:     for (int k = 0; k < kc; ++k) {
	leaq	8(%rsi), %rcx	#, tmp615
	addq	$256, %rdx	#, ivtmp.35
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	1(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 1B], tmp344
	vpbroadcastb	5(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 5B], tmp412
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp343, tmp345
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	7(%rsi), %zmm17	# MEM[(const uint8_t *)_280 + 7B], tmp446
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp345
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp352
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	3(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 3B], tmp378
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp352, tmp357
	vpopcntb	%zmm0, %zmm0	# tmp345, tmp350
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp357, tmp350, _135
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	2(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 2B], tmp377
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm13	# tmp359, tmp363
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _135, tmp368
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp368, tmp372
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm11, %zmm13, %zmm11	# acc_I_I_lsm.22, tmp363, acc_I_I_lsm.22
	vpaddw	%zmm10, %zmm0, %zmm10	# acc_I_I_lsm.23, tmp372, acc_I_I_lsm.23
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp377, tmp379
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp386
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp386, tmp391
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp379
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	9(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 1B], tmp344
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp379, tmp384
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp391, tmp384, _180
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	4(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 4B], tmp411
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm15	# tmp393, tmp397
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _180, tmp402
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp402, tmp406
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm9, %zmm15, %zmm9	# acc_I_I_lsm.24, tmp397, acc_I_I_lsm.24
	vpaddw	%zmm8, %zmm0, %zmm8	# acc_I_I_lsm.25, tmp406, acc_I_I_lsm.25
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp411, tmp413
	vpternlogq	$228, %zmm12, %zmm14, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp420
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp420, tmp425
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm14, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp413
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	6(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 6B], tmp445
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp413, tmp418
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp425, tmp418, _225
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm1	# tmp427, tmp431
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _225, tmp436
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm7, %zmm1, %zmm7	# acc_I_I_lsm.26, tmp431, acc_I_I_lsm.26
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm14, %zmm1	# tmp445, tmp447
	vpternlogq	$228, %zmm12, %zmm17, %zmm14	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp454
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm14, %zmm14	# tmp454, tmp459
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm17, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp447
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp436, tmp440
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	15(%rsi), %zmm17	# MEM[(const uint8_t *)_280 + 7B], tmp446
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp447, tmp452
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm6, %zmm0, %zmm6	# acc_I_I_lsm.27, tmp440, acc_I_I_lsm.27
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm14, %zmm1, %zmm1	# tmp459, tmp452, _270
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	13(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 5B], tmp412
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm12	# tmp461, tmp465
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm1, %ymm1	# _270, tmp470
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm1	# tmp470, tmp474
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm5, %zmm12, %zmm5	# acc_I_I_lsm.28, tmp465, acc_I_I_lsm.28
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6501:   return *(__m512i_u *)__P;
	vmovdqu64	-192(%rdx), %zmm12	# MEM[(__m512i_u * {ref-all})_62], MEM[(__m512i_u * {ref-all})_62]
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm4, %zmm1, %zmm4	# acc_I_I_lsm.29, tmp474, acc_I_I_lsm.29
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	8(%rsi), %zmm1	# MEM[(const uint8_t *)_280], tmp343
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp343, tmp345
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp352
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp352, tmp357
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp345
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	11(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 3B], tmp378
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp345, tmp350
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp357, tmp350, _135
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	10(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 2B], tmp377
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm13	# tmp359, tmp363
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _135, tmp368
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp368, tmp372
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm11, %zmm13, %zmm11	# acc_I_I_lsm.22, tmp363, acc_I_I_lsm.22
	vpaddw	%zmm10, %zmm0, %zmm10	# acc_I_I_lsm.23, tmp372, acc_I_I_lsm.23
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp377, tmp379
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp386
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp386, tmp391
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp379
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	17(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 1B], tmp344
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp379, tmp384
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp391, tmp384, _180
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	12(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 4B], tmp411
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm15	# tmp393, tmp397
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _180, tmp402
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp402, tmp406
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm9, %zmm15, %zmm9	# acc_I_I_lsm.24, tmp397, acc_I_I_lsm.24
	vpaddw	%zmm8, %zmm0, %zmm8	# acc_I_I_lsm.25, tmp406, acc_I_I_lsm.25
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp411, tmp413
	vpternlogq	$228, %zmm12, %zmm14, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp420
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp420, tmp425
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm14, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp413
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	14(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 6B], tmp445
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp413, tmp418
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp425, tmp418, _225
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm1	# tmp427, tmp431
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _225, tmp436
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm7, %zmm1, %zmm7	# acc_I_I_lsm.26, tmp431, acc_I_I_lsm.26
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm14, %zmm1	# tmp445, tmp447
	vpternlogq	$228, %zmm12, %zmm17, %zmm14	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp454
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm14, %zmm14	# tmp454, tmp459
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm17, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp447
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp436, tmp440
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	23(%rsi), %zmm17	# MEM[(const uint8_t *)_280 + 7B], tmp446
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp447, tmp452
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm6, %zmm0, %zmm6	# acc_I_I_lsm.27, tmp440, acc_I_I_lsm.27
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm14, %zmm1, %zmm1	# tmp459, tmp452, _270
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	21(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 5B], tmp412
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm12	# tmp461, tmp465
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm1, %ymm1	# _270, tmp470
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm1	# tmp470, tmp474
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm5, %zmm12, %zmm5	# acc_I_I_lsm.28, tmp465, acc_I_I_lsm.28
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6501:   return *(__m512i_u *)__P;
	vmovdqu64	-128(%rdx), %zmm12	# MEM[(__m512i_u * {ref-all})_62], MEM[(__m512i_u * {ref-all})_62]
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm4, %zmm1, %zmm4	# acc_I_I_lsm.29, tmp474, acc_I_I_lsm.29
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	16(%rsi), %zmm1	# MEM[(const uint8_t *)_280], tmp343
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp343, tmp345
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp352
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp352, tmp357
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp345
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	19(%rsi), %zmm2	# MEM[(const uint8_t *)_280 + 3B], tmp378
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp345, tmp350
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp357, tmp350, _135
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	18(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 2B], tmp377
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm13	# tmp359, tmp363
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _135, tmp368
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp368, tmp372
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm11, %zmm13, %zmm11	# acc_I_I_lsm.22, tmp363, acc_I_I_lsm.22
	vpaddw	%zmm10, %zmm0, %zmm10	# acc_I_I_lsm.23, tmp372, acc_I_I_lsm.23
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp377, tmp379
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp386
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp386, tmp391
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp379
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	17(%rcx), %zmm2	# MEM[(const uint8_t *)_280 + 1B], tmp344
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp379, tmp384
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp391, tmp384, _180
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	20(%rsi), %zmm1	# MEM[(const uint8_t *)_280 + 4B], tmp411
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm15	# tmp393, tmp397
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _180, tmp402
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp402, tmp406
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm9, %zmm15, %zmm9	# acc_I_I_lsm.24, tmp397, acc_I_I_lsm.24
	vpaddw	%zmm8, %zmm0, %zmm8	# acc_I_I_lsm.25, tmp406, acc_I_I_lsm.25
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp411, tmp413
	vpternlogq	$228, %zmm12, %zmm14, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp420
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp420, tmp425
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm14, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp413
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	22(%rsi), %zmm14	# MEM[(const uint8_t *)_280 + 6B], tmp445
# scripts/exp2_kernel_only.cpp:21:     for (int k = 0; k < kc; ++k) {
	leaq	24(%rcx), %rsi	#, ivtmp.36
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp413, tmp418
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp425, tmp418, _225
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm1	# tmp427, tmp431
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _225, tmp436
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm7, %zmm1, %zmm7	# acc_I_I_lsm.26, tmp431, acc_I_I_lsm.26
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm14, %zmm1	# tmp445, tmp447
	vpternlogq	$228, %zmm12, %zmm17, %zmm14	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp454
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm14, %zmm14	# tmp454, tmp459
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm17, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp447
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp436, tmp440
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp447, tmp452
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm6, %zmm0, %zmm6	# acc_I_I_lsm.27, tmp440, acc_I_I_lsm.27
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm14, %zmm1, %zmm1	# tmp459, tmp452, _270
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm12	# tmp461, tmp465
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm1, %ymm1	# _270, tmp470
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm1	# tmp470, tmp474
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm5, %zmm12, %zmm5	# acc_I_I_lsm.28, tmp465, acc_I_I_lsm.28
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6501:   return *(__m512i_u *)__P;
	vmovdqu64	-64(%rdx), %zmm12	# MEM[(__m512i_u * {ref-all})_62], MEM[(__m512i_u * {ref-all})_62]
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm4, %zmm1, %zmm4	# acc_I_I_lsm.29, tmp474, acc_I_I_lsm.29
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	16(%rcx), %zmm1	# MEM[(const uint8_t *)_280], tmp343
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp343, tmp345
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp352
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp352, tmp357
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp344, tmp345
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	19(%rcx), %zmm2	# MEM[(const uint8_t *)_280 + 3B], tmp378
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp345, tmp350
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp357, tmp350, _135
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	18(%rcx), %zmm1	# MEM[(const uint8_t *)_280 + 2B], tmp377
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm13	# tmp359, tmp363
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _135, tmp368
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp368, tmp372
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm11, %zmm13, %zmm13	# acc_I_I_lsm.22, tmp363, tmp367
	vpaddw	%zmm10, %zmm0, %zmm3	# acc_I_I_lsm.23, tmp372, tmp376
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp377, tmp379
	vpternlogq	$228, %zmm12, %zmm2, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp386
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp386, tmp391
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm2, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp378, tmp379
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm13, %zmm11	# tmp367, acc_I_I_lsm.22
	vmovdqa64	%zmm3, %zmm10	# tmp376, acc_I_I_lsm.23
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp379, tmp384
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp391, tmp384, _180
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	20(%rcx), %zmm1	# MEM[(const uint8_t *)_280 + 4B], tmp411
	vpbroadcastb	21(%rcx), %zmm14	# MEM[(const uint8_t *)_280 + 5B], tmp412
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm15	# tmp393, tmp397
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _180, tmp402
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	23(%rcx), %zmm17	# MEM[(const uint8_t *)_280 + 7B], tmp446
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp402, tmp406
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm9, %zmm15, %zmm15	# acc_I_I_lsm.24, tmp397, tmp401
	vpaddw	%zmm8, %zmm0, %zmm2	# acc_I_I_lsm.25, tmp406, tmp410
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm1, %zmm0	# tmp411, tmp413
	vpternlogq	$228, %zmm12, %zmm14, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp420
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp420, tmp425
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm14, %zmm0	#, MEM[(__m512i_u * {ref-all})_62], tmp412, tmp413
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:225:   return __extension__ (__m512i)(__v64qi)
	vpbroadcastb	22(%rcx), %zmm14	# MEM[(const uint8_t *)_280 + 6B], tmp445
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm15, %zmm9	# tmp401, acc_I_I_lsm.24
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm0, %zmm0	# tmp413, tmp418
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm2, %zmm8	# tmp410, acc_I_I_lsm.25
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm1, %zmm0, %zmm0	# tmp425, tmp418, _225
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm1	# tmp427, tmp431
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _225, tmp436
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm7, %zmm1, %zmm16	# acc_I_I_lsm.26, tmp431, tmp435
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vmovdqa64	%zmm14, %zmm1	# tmp445, tmp447
	vpternlogq	$228, %zmm12, %zmm17, %zmm14	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp454
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm14, %zmm14	# tmp454, tmp459
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:1666:   return (__m512i)
	vpternlogq	$216, %zmm12, %zmm17, %zmm1	#, MEM[(__m512i_u * {ref-all})_62], tmp446, tmp447
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm0, %zmm0	# tmp436, tmp440
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm16, %zmm7	# tmp435, acc_I_I_lsm.26
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bitalgintrin.h:41:   return (__m512i) __builtin_ia32_vpopcountb_v64qi ((__v64qi) __A);
	vpopcntb	%zmm1, %zmm1	# tmp447, tmp452
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm6, %zmm0, %zmm0	# acc_I_I_lsm.27, tmp440, tmp444
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm0, %zmm6	# tmp444, acc_I_I_lsm.27
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:987:   return (__m512i) ((__v64qu) __A - (__v64qu) __B);
	vpsubb	%zmm14, %zmm1, %zmm1	# tmp459, tmp452, _270
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm12	# tmp461, tmp465
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm1, %ymm1	# _270, tmp470
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:783:   return (__m512i) __builtin_ia32_pmovsxbw512_mask ((__v32qi) __A,
	vpmovsxbw	%ymm1, %zmm1	# tmp470, tmp474
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vpaddw	%zmm5, %zmm12, %zmm12	# acc_I_I_lsm.28, tmp465, tmp469
	vpaddw	%zmm4, %zmm1, %zmm1	# acc_I_I_lsm.29, tmp474, tmp478
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512bwintrin.h:1276:   return (__m512i) ((__v32hu) __A + (__v32hu) __B);
	vmovdqa64	%zmm12, %zmm5	# tmp469, acc_I_I_lsm.28
	vmovdqa64	%zmm1, %zmm4	# tmp478, acc_I_I_lsm.29
# scripts/exp2_kernel_only.cpp:21:     for (int k = 0; k < kc; ++k) {
	cmpq	%rsi, %r9	# ivtmp.36, _245
	jne	.L3	#,
.L21:
	vmovdqa64	%zmm13, (%rsp)	# tmp367, acc[0][0]
	vmovdqa64	%zmm3, 64(%rsp)	# tmp376, acc[0][1]
	vmovdqa64	%zmm15, 128(%rsp)	# tmp401, acc[1][0]
	vmovdqa64	%zmm2, 192(%rsp)	# tmp410, acc[1][1]
	vmovdqa64	%zmm16, 256(%rsp)	# tmp435, acc[2][0]
	vmovdqa64	%zmm0, 320(%rsp)	# tmp444, acc[2][1]
	vmovdqa64	%zmm12, 384(%rsp)	# tmp469, acc[3][0]
	vmovdqa64	%zmm1, 448(%rsp)	# tmp478, acc[3][1]
.L2:
# scripts/exp2_kernel_only.cpp:44:         _mm512_storeu_si512((__m512i*)(Cr +  0),
	vmovdqa64	(%rsp), %zmm0	# acc[0][0], _211
# scripts/exp2_kernel_only.cpp:43:         int* Cr = C + r * m;
	movslq	%r8d, %rdx	# m, m
# scripts/exp2_kernel_only.cpp:43:         int* Cr = C + r * m;
	salq	$2, %rdx	#, _10
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm1	# tmp479, tmp483
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _211, tmp487
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm0	# tmp487, tmp491
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6534:   *(__m512i_u *)__P = __A;
	vmovdqu64	%zmm1, (%rax)	# tmp483, MEM[(__m512i_u * {ref-all})C_34(D)]
	vmovdqu64	%zmm0, 64(%rax)	# tmp491, MEM[(__m512i_u * {ref-all})C_34(D) + 64B]
# scripts/exp2_kernel_only.cpp:48:         _mm512_storeu_si512((__m512i*)(Cr + 32),
	vmovdqa64	64(%rsp), %zmm0	# acc[0][1], _116
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm1	# tmp495, tmp499
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _116, tmp503
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm0	# tmp503, tmp507
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6534:   *(__m512i_u *)__P = __A;
	vmovdqu64	%zmm1, 128(%rax)	# tmp499, MEM[(__m512i_u * {ref-all})C_34(D) + 128B]
	vmovdqu64	%zmm0, 192(%rax)	# tmp507, MEM[(__m512i_u * {ref-all})C_34(D) + 192B]
# scripts/exp2_kernel_only.cpp:44:         _mm512_storeu_si512((__m512i*)(Cr +  0),
	vmovdqa64	128(%rsp), %zmm0	# acc[1][0], _36
# scripts/exp2_kernel_only.cpp:43:         int* Cr = C + r * m;
	addq	%rdx, %rax	# _10, Cr
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm1	# tmp512, tmp516
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _36, tmp520
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm0	# tmp520, tmp524
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6534:   *(__m512i_u *)__P = __A;
	vmovdqu64	%zmm1, (%rax)	# tmp516, MEM[(__m512i_u * {ref-all})Cr_150]
	vmovdqu64	%zmm0, 64(%rax)	# tmp524, MEM[(__m512i_u * {ref-all})Cr_150 + 64B]
# scripts/exp2_kernel_only.cpp:48:         _mm512_storeu_si512((__m512i*)(Cr + 32),
	vmovdqa64	192(%rsp), %zmm0	# acc[1][1], _47
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm1	# tmp528, tmp532
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _47, tmp536
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm0	# tmp536, tmp540
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6534:   *(__m512i_u *)__P = __A;
	vmovdqu64	%zmm1, 128(%rax)	# tmp532, MEM[(__m512i_u * {ref-all})Cr_150 + 128B]
	vmovdqu64	%zmm0, 192(%rax)	# tmp540, MEM[(__m512i_u * {ref-all})Cr_150 + 192B]
# scripts/exp2_kernel_only.cpp:44:         _mm512_storeu_si512((__m512i*)(Cr +  0),
	vmovdqa64	256(%rsp), %zmm0	# acc[2][0], _324
# scripts/exp2_kernel_only.cpp:43:         int* Cr = C + r * m;
	addq	%rdx, %rax	# _10, Cr
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm1	# tmp544, tmp548
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _324, tmp552
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm0	# tmp552, tmp556
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6534:   *(__m512i_u *)__P = __A;
	vmovdqu64	%zmm1, (%rax)	# tmp548, MEM[(__m512i_u * {ref-all})Cr_323]
	vmovdqu64	%zmm0, 64(%rax)	# tmp556, MEM[(__m512i_u * {ref-all})Cr_323 + 64B]
# scripts/exp2_kernel_only.cpp:48:         _mm512_storeu_si512((__m512i*)(Cr + 32),
	vmovdqa64	320(%rsp), %zmm0	# acc[2][1], _339
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm1	# tmp560, tmp564
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _339, tmp568
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm0	# tmp568, tmp572
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6534:   *(__m512i_u *)__P = __A;
	vmovdqu64	%zmm1, 128(%rax)	# tmp564, MEM[(__m512i_u * {ref-all})Cr_323 + 128B]
	vmovdqu64	%zmm0, 192(%rax)	# tmp572, MEM[(__m512i_u * {ref-all})Cr_323 + 192B]
# scripts/exp2_kernel_only.cpp:44:         _mm512_storeu_si512((__m512i*)(Cr +  0),
	vmovdqa64	384(%rsp), %zmm0	# acc[3][0], _20
# scripts/exp2_kernel_only.cpp:43:         int* Cr = C + r * m;
	addq	%rdx, %rax	# _10, Cr
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm1	# tmp576, tmp580
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _20, tmp584
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm0	# tmp584, tmp588
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6534:   *(__m512i_u *)__P = __A;
	vmovdqu64	%zmm1, (%rax)	# tmp580, MEM[(__m512i_u * {ref-all})Cr_35]
	vmovdqu64	%zmm0, 64(%rax)	# tmp588, MEM[(__m512i_u * {ref-all})Cr_35 + 64B]
# scripts/exp2_kernel_only.cpp:48:         _mm512_storeu_si512((__m512i*)(Cr + 32),
	vmovdqa64	448(%rsp), %zmm0	# acc[3][1], _21
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm1	# tmp592, tmp596
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512dqintrin.h:2066:   return (__m256i) __builtin_ia32_extracti32x8_mask ((__v16si) __A,
	vextracti32x8	$0x1, %zmm0, %ymm0	# _21, tmp600
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:2252:   return (__m512i) __builtin_ia32_pmovsxwd512_mask ((__v16hi) __A,
	vpmovsxwd	%ymm0, %zmm0	# tmp600, tmp604
# /usr/lib/gcc/x86_64-linux-gnu/13/include/avx512fintrin.h:6534:   *(__m512i_u *)__P = __A;
	vmovdqu64	%zmm1, 128(%rax)	# tmp596, MEM[(__m512i_u * {ref-all})Cr_35 + 128B]
	vmovdqu64	%zmm0, 192(%rax)	# tmp604, MEM[(__m512i_u * {ref-all})Cr_35 + 192B]
# scripts/exp2_kernel_only.cpp:53: }
	movq	568(%rsp), %rax	# D.39099, tmp622
	subq	%fs:40, %rax	# MEM[(<address-space-1> long unsigned int *)40B], tmp622
	jne	.L25	#,
	vzeroupper
	leave	
	.cfi_remember_state
	.cfi_def_cfa 7, 8
	ret	
.L25:
	.cfi_restore_state
	vzeroupper
	call	__stack_chk_fail@PLT	#
	.cfi_endproc
.LFE6442:
	.size	_Z17micro_kernel_4x64iPKhS0_Pii, .-_Z17micro_kernel_4x64iPKhS0_Pii
	.ident	"GCC: (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0"
	.section	.note.GNU-stack,"",@progbits
	.section	.note.gnu.property,"a"
	.align 8
	.long	1f - 0f
	.long	4f - 1f
	.long	5
0:
	.string	"GNU"
1:
	.align 8
	.long	0xc0000002
	.long	3f - 2f
2:
	.long	0x3
3:
	.align 8
4:
