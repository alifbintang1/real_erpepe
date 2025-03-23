# benchmarking.py
import time
import os
import psutil
import matplotlib.pyplot as plt
from cnf_parser import parse_cnf
from resolvent_generator import generate_resolvents_minimal, generate_resolvents
from res_sat import res_sat
from validator import validate_interpretation
import pandas as pd
import numpy as np
import argparse

def measure_performance(cnf_file, use_minimal=True, verbose=True):
    """
    Mengukur performa algoritma RES-SAT untuk sebuah file CNF.
    
    Args:
        cnf_file: Path ke file CNF
        use_minimal: Boolean untuk menentukan apakah menggunakan resolvent minimal
        verbose: Boolean untuk menentukan apakah output detail ditampilkan
    
    Returns:
        Dictionary berisi metrik performa
    """
    # Ukur penggunaan memori awal
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss / 1024 / 1024  # dalam MB
    
    # Parse file CNF
    start_time = time.time()
    num_vars, clauses, _ = parse_cnf(cnf_file)
    parse_time = time.time() - start_time
    
    if verbose:
        print(f"File: {cnf_file}")
        print(f"Jumlah variabel: {num_vars}")
        print(f"Jumlah klausa awal: {len(clauses)}")
    
    # Generasi resolvent
    start_time = time.time()
    if use_minimal:
        R = generate_resolvents_minimal(clauses)
    else:
        R = generate_resolvents(clauses)
    resolvent_time = time.time() - start_time
    
    if verbose:
        print(f"Jumlah klausa setelah resolusi: {len(R)}")
    
    # Jalankan RES-SAT
    start_time = time.time()
    interpretation = res_sat(R, num_vars)
    res_sat_time = time.time() - start_time
    
    # Ukur penggunaan memori akhir
    end_memory = process.memory_info().rss / 1024 / 1024  # dalam MB
    memory_used = end_memory - start_memory
    
    # Validasi hasil
    start_time = time.time()
    valid = validate_interpretation(clauses, interpretation)
    validation_time = time.time() - start_time
    
    if verbose:
        print(f"Interpretasi valid: {valid}")
        print(f"Waktu parsing: {parse_time:.4f} detik")
        print(f"Waktu resolusi: {resolvent_time:.4f} detik")
        print(f"Waktu RES-SAT: {res_sat_time:.4f} detik")
        print(f"Waktu validasi: {validation_time:.4f} detik")
        print(f"Total waktu: {parse_time + resolvent_time + res_sat_time + validation_time:.4f} detik")
        print(f"Penggunaan memori: {memory_used:.2f} MB")
    
    return {
        "file": os.path.basename(cnf_file),
        "num_vars": num_vars,
        "num_clauses_orig": len(clauses),
        "num_clauses_res": len(R),
        "parse_time": parse_time,
        "resolvent_time": resolvent_time,
        "res_sat_time": res_sat_time,
        "validation_time": validation_time,
        "total_time": parse_time + resolvent_time + res_sat_time + validation_time,
        "memory_used": memory_used,
        "valid": valid,
        "method": "minimal" if use_minimal else "standard"
    }

def compare_methods(cnf_file, output_file=None):
    """
    Membandingkan performa metode standard dan minimal pada file CNF.
    
    Args:
        cnf_file: Path ke file CNF
        output_file: Path untuk menyimpan hasil perbandingan (opsional)
    """
    print(f"Membandingkan metode untuk file: {cnf_file}")
    
    print("\n=== Metode Resolvent Minimal ===")
    minimal_result = measure_performance(cnf_file, use_minimal=True)
    
    print("\n=== Metode Resolvent Standard ===")
    standard_result = measure_performance(cnf_file, use_minimal=False)
    
    # Bandingkan hasil
    print("\n=== Perbandingan ===")
    print(f"Jumlah klausa resolvent (minimal): {minimal_result['num_clauses_res']}")
    print(f"Jumlah klausa resolvent (standard): {standard_result['num_clauses_res']}")
    print(f"Pengurangan jumlah klausa: {standard_result['num_clauses_res'] - minimal_result['num_clauses_res']} ({(1 - minimal_result['num_clauses_res'] / standard_result['num_clauses_res']) * 100:.2f}%)")
    
    print(f"\nWaktu resolusi (minimal): {minimal_result['resolvent_time']:.4f} detik")
    print(f"Waktu resolusi (standard): {standard_result['resolvent_time']:.4f} detik")
    
    print(f"\nWaktu total (minimal): {minimal_result['total_time']:.4f} detik")
    print(f"Waktu total (standard): {standard_result['total_time']:.4f} detik")
    
    print(f"\nPenggunaan memori (minimal): {minimal_result['memory_used']:.2f} MB")
    print(f"Penggunaan memori (standard): {standard_result['memory_used']:.2f} MB")
    
    # Visualisasi perbandingan
    create_comparison_plots(minimal_result, standard_result)
    
    # Simpan hasil jika diminta
    if output_file:
        results_df = pd.DataFrame([minimal_result, standard_result])
        results_df.to_csv(output_file, index=False)
        print(f"Hasil disimpan ke {output_file}")

def create_comparison_plots(minimal_result, standard_result):
    """
    Membuat visualisasi perbandingan antara metode minimal dan standard.
    
    Args:
        minimal_result: Hasil pengukuran dengan metode minimal
        standard_result: Hasil pengukuran dengan metode standard
    """
    # Persiapkan data
    methods = ['Minimal', 'Standard']
    
    # Data waktu per tahap
    time_data = {
        'Parsing': [minimal_result['parse_time'], standard_result['parse_time']],
        'Resolusi': [minimal_result['resolvent_time'], standard_result['resolvent_time']],
        'RES-SAT': [minimal_result['res_sat_time'], standard_result['res_sat_time']],
        'Validasi': [minimal_result['validation_time'], standard_result['validation_time']]
    }
    
    # Data penggunaan memori
    memory_data = [minimal_result['memory_used'], standard_result['memory_used']]
    
    # Data jumlah klausa
    clauses_data = {
        'Original': [minimal_result['num_clauses_orig'], standard_result['num_clauses_orig']],
        'Resolusi': [minimal_result['num_clauses_res'], standard_result['num_clauses_res']]
    }
    
    # Buat plot
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Waktu eksekusi per tahap
    plt.subplot(2, 2, 1)
    df_time = pd.DataFrame(time_data, index=methods)
    df_time.plot(kind='bar', ax=plt.gca())
    plt.title('Waktu Eksekusi per Tahap')
    plt.ylabel('Waktu (detik)')
    plt.xticks(rotation=0)
    
    # Plot 2: Waktu total
    plt.subplot(2, 2, 2)
    total_times = [minimal_result['total_time'], standard_result['total_time']]
    plt.bar(methods, total_times, color=['blue', 'orange'])
    plt.title('Waktu Total Eksekusi')
    plt.ylabel('Waktu (detik)')
    
    # Plot 3: Penggunaan memori
    plt.subplot(2, 2, 3)
    plt.bar(methods, memory_data, color=['blue', 'orange'])
    plt.title('Penggunaan Memori')
    plt.ylabel('Memori (MB)')
    
    # Plot 4: Jumlah klausa
    plt.subplot(2, 2, 4)
    df_clauses = pd.DataFrame(clauses_data, index=methods)
    df_clauses.plot(kind='bar', ax=plt.gca())
    plt.title('Jumlah Klausa')
    plt.ylabel('Jumlah')
    plt.xticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig('comparison_results.png')
    print("Visualisasi perbandingan disimpan ke comparison_results.png")
    plt.close()

def run_multiple_tests(cnf_file, num_runs=5, use_minimal=True, output_file=None):
    """
    Menjalankan beberapa kali pengujian pada file CNF yang sama untuk
    mendapatkan statistik performa yang lebih akurat.
    
    Args:
        cnf_file: Path ke file CNF
        num_runs: Jumlah pengujian yang dilakukan
        use_minimal: Boolean untuk menentukan metode resolvent
        output_file: Path untuk menyimpan hasil (opsional)
    """
    print(f"Menjalankan {num_runs} kali pengujian pada file: {cnf_file}")
    print(f"Metode: {'Minimal' if use_minimal else 'Standard'}")
    
    results = []
    
    for i in range(num_runs):
        print(f"\nPengujian ke-{i+1}:")
        result = measure_performance(cnf_file, use_minimal=use_minimal, verbose=False)
        results.append(result)
        print(f"  Waktu: {result['total_time']:.4f}s, Memori: {result['memory_used']:.2f}MB")
    
    # Buat DataFrame dari hasil
    df = pd.DataFrame(results)
    
    # Hitung statistik
    stats = {
        'parse_time': {
            'mean': df['parse_time'].mean(),
            'std': df['parse_time'].std(),
            'min': df['parse_time'].min(),
            'max': df['parse_time'].max()
        },
        'resolvent_time': {
            'mean': df['resolvent_time'].mean(),
            'std': df['resolvent_time'].std(),
            'min': df['resolvent_time'].min(),
            'max': df['resolvent_time'].max()
        },
        'res_sat_time': {
            'mean': df['res_sat_time'].mean(),
            'std': df['res_sat_time'].std(),
            'min': df['res_sat_time'].min(),
            'max': df['res_sat_time'].max()
        },
        'total_time': {
            'mean': df['total_time'].mean(),
            'std': df['total_time'].std(),
            'min': df['total_time'].min(),
            'max': df['total_time'].max()
        },
        'memory_used': {
            'mean': df['memory_used'].mean(),
            'std': df['memory_used'].std(),
            'min': df['memory_used'].min(),
            'max': df['memory_used'].max()
        }
    }
    
    # Tampilkan statistik
    print("\nStatistik hasil pengujian:")
    print(f"Waktu parsing: {stats['parse_time']['mean']:.4f} ± {stats['parse_time']['std']:.4f} detik")
    print(f"Waktu resolusi: {stats['resolvent_time']['mean']:.4f} ± {stats['resolvent_time']['std']:.4f} detik")
    print(f"Waktu RES-SAT: {stats['res_sat_time']['mean']:.4f} ± {stats['res_sat_time']['std']:.4f} detik")
    print(f"Waktu total: {stats['total_time']['mean']:.4f} ± {stats['total_time']['std']:.4f} detik")
    print(f"Penggunaan memori: {stats['memory_used']['mean']:.2f} ± {stats['memory_used']['std']:.2f} MB")
    
    # Visualisasikan hasil
    create_multiple_runs_plot(df)
    
    # Simpan hasil jika diminta
    if output_file:
        df.to_csv(output_file, index=False)
        print(f"Hasil disimpan ke {output_file}")
    
    return stats

def create_multiple_runs_plot(df):
    """
    Membuat visualisasi hasil beberapa kali pengujian.
    
    Args:
        df: DataFrame berisi hasil beberapa kali pengujian
    """
    plt.figure(figsize=(12, 8))
    
    # Plot 1: Waktu eksekusi per pengujian
    plt.subplot(2, 2, 1)
    runs = range(1, len(df) + 1)
    plt.plot(runs, df['total_time'], 'o-', label='Total')
    plt.plot(runs, df['resolvent_time'], 'o-', label='Resolusi')
    plt.plot(runs, df['res_sat_time'], 'o-', label='RES-SAT')
    plt.plot(runs, df['parse_time'], 'o-', label='Parsing')
    plt.title('Waktu Eksekusi per Pengujian')
    plt.xlabel('Pengujian ke-')
    plt.ylabel('Waktu (detik)')
    plt.legend()
    plt.grid(True)
    
    # Plot 2: Penggunaan memori per pengujian
    plt.subplot(2, 2, 2)
    plt.plot(runs, df['memory_used'], 'o-', color='green')
    plt.title('Penggunaan Memori per Pengujian')
    plt.xlabel('Pengujian ke-')
    plt.ylabel('Memori (MB)')
    plt.grid(True)
    
    # Plot 3: Distribusi waktu eksekusi
    plt.subplot(2, 2, 3)
    plt.boxplot([df['parse_time'], df['resolvent_time'], df['res_sat_time'], df['total_time']],
               labels=['Parsing', 'Resolusi', 'RES-SAT', 'Total'])
    plt.title('Distribusi Waktu Eksekusi')
    plt.ylabel('Waktu (detik)')
    plt.grid(True)
    
    # Plot 4: Distribusi penggunaan memori
    plt.subplot(2, 2, 4)
    plt.boxplot(df['memory_used'])
    plt.title('Distribusi Penggunaan Memori')
    plt.ylabel('Memori (MB)')
    plt.xticks([1], ['Memori'])
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('multiple_runs_results.png')
    print("Visualisasi hasil beberapa pengujian disimpan ke multiple_runs_results.png")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="RES-SAT Performance Evaluation Tool")
    parser.add_argument("--file", default="success_examples/aim-50-1_6-yes1-4_simplified.cnf", 
                      help="Path to CNF file for benchmarking")
    parser.add_argument("--compare", action="store_true", 
                      help="Compare minimal vs standard resolvent methods")
    parser.add_argument("--runs", type=int, default=5, 
                      help="Number of runs for statistical analysis")
    parser.add_argument("--output", default=None, 
                      help="Output file for benchmark results")
    parser.add_argument("--standard", action="store_true", 
                      help="Use standard resolvent generation (default: minimal)")
    
    args = parser.parse_args()
    
    # Verifikasi file CNF
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} tidak ditemukan")
        return
    
    if args.compare:
        compare_methods(args.file, args.output)
    else:
        if args.runs > 1:
            run_multiple_tests(args.file, num_runs=args.runs, 
                            use_minimal=not args.standard, output_file=args.output)
        else:
            measure_performance(args.file, use_minimal=not args.standard)

if __name__ == "__main__":
    main()