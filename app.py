from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import warnings
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

warnings.filterwarnings("ignore")

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="BEI Multi-Timeframe Screener", 
    page_icon="🚀", 
    layout="wide"
)

st.title("🚀 BEI Multi-Timeframe Breakout & Accumulation Screener")
st.caption("Pindai 900+ emiten IDX dengan pilihan interval waktu: Daily (1D), 1 Jam (1H), hingga 15 Menit (15m).")

# Sidebar Pengaturan
st.sidebar.header("⚙️ Pengaturan Screener")

# Pilihan Interval Waktu
interval_opt = st.sidebar.selectbox(
    "Interval Waktu", 
    ["1d (Harian / Daily)", "1h (1 Jam)", "15m (15 Menit)"], 
    index=0
)

# Otomatis menyesuaikan period berdasarkan interval (karena batasan Yahoo Finance)
if "15m" in interval_opt:
    interval = "15m"
    period = "5d"   # Maksimal aman untuk 15m di yfinance
    st.sidebar.info("ℹ️ Interval 15m menggunakan data 5 hari terakhir (batasan Yahoo Finance).")
elif "1h" in interval_opt:
    interval = "1h"
    period = "60d"  # Aman untuk 1 jam
    st.sidebar.info("ℹ️ Interval 1h menggunakan data 60 hari terakhir.")
else:
    interval = "1d"
    period = "1y"   # 1 tahun untuk daily

min_value_rp = st.sidebar.number_input("Min. Nilai Transaksi (Rp Juta)", min_value=10, value=100) * 1_000_000
max_workers = st.sidebar.slider("Kecepatan Scan (Threads)", min_value=4, max_value=16, value=12)

# Daftar lengkap seluruh emiten IDX (900+ saham)
RAW_TICKERS = [
    "ROTI", "MGLV", "TRUE", "LABA", "ARCI", "IPAC", "MASB", "BMHS", "FLMC", "NICL", "UVCR", "BUKA", "HAIS", "OILS", "GPSO", "MCOL", "RSGK", "RUNS", "SBMA", "CMNT", "GTSI", "IDEA", "KUAS", "BOBA", "MTEL", "DEPO", "BINO", "CMRY", "WGSH", "TAYS", "WMPP", "RMKE", "OBMD", "AVIA", "IPPE", "NASI", "BSML", "DRMA", "ADMR", "SEMA", "ASLC", "NETV", "BAUT", "ENAK", "NTBK", "SMKM", "STAA", "NANO", "BIKE", "WIRG", "SICO", "GOTO", "TLDN", "MTMH", "WINR", "IBOS", "OLIV", "ASHA", "SWID", "TRGU", "ARKO", "CHEM", "DEWI", "AXIO", "KRYA", "HATM", "RCCC", "GULA", "JARR", "AMMS", "RAFI", "KKES", "ELPI", "EURO", "KLIN", "TOOL", "BUAH", "CRAB", "MEDS", "COAL", "PRAY", "CBUT", "BELI", "MKTR", "OMED", "BSBK", "PDPP", "KDTN", "ZATA", "NINE", "MMIX", "PADA", "ISAP", "VTNY", "SOUL", "ELIT", "BEER", "CBPE", "SUNI", "CBRE", "WINE", "BMBL", "PEVE", "LAJU", "FWCT", "NAYZ", "IRSX", "PACK", "VAST", "CHIP", "HALO", "KING", "PGEO", "FUTR", "HILL", "BDKR", "PTMP", "SAGE", "TRON", "CUAN", "NSSS", "GTRA", "HAJJ", "PIPA", "NCKL", "MENN", "AWAN", "MBMA", "RAAM", "DOOH", "JATI", "TYRE", "MPXL", "SMIL", "KLAS", "MAXI", "VKTR", "RELF", "AMMN", "CRSN", "GRPM", "WIDI", "TGUK", "INET", "MAHA", "RMKO", "CNMA", "FOLK", "HBAT", "GRIA", "PPRI", "ERAL", "CYBR", "MUTU", "LMAX", "HUMI", "MSIE", "RSCH", "BABY", "AEGS", "IOTF", "KOCI", "PTPS", "BREN", "STRK", "KOKA", "LOPI", "UDNG", "RGAS", "MSTI", "IKPM", "AYAM", "SURI", "ASLI", "CGAS", "NICE", "MSJA", "SMLE", "ACRO", "MANG", "GRPH", "SMGA", "UNTD", "TOSK", "MPIX", "ALII", "MKAP", "MEJA", "LIVE", "HYGN", "BAIK", "VISI", "AREA", "MHKI", "ATLA", "DATA", "SOLA", "BATR", "SPRE", "PART", "GOLF", "ISEA", "BLES", "GUNA", "LABS", "DOSS", "NEST", "PTMR", "VERN", "DAAZ", "BOAT", "NAIK", "AADI", "MDIY", "KSIX", "RATU", "YOII", "HGII", "BRRC", "DGWG", "CBDK", "OBAT", "MINE", "KAQI", "YUPI", "FORE", "MDLA", "DKHH", "ASPR", "PSAT", "COIN", "CDIA", "BLOG", "MERI", "CHEK", "PMUI", "EMAS", "PJHB", "RLCO", "SUPA", "WBSA", "JECX", "JELI", "EMMI", "BACH", "PRDL", "RANS", "AALI", "ABBA", "ABDA", "ABMM", "ACES", "ACST", "ADES", "ADHI", "ADMF", "ADMG", "ADRO", "AGII", "AGRO", "AGRS", "AHAP", "CASH", "TECH", "BSSR", "BSWD", "BTEK", "BTEL", "BTON", "BTPN", "BUDI", "AIMS", "AISA", "AKKU", "AKPI", "AKRA", "AKSI", "ALDO", "ALKA", "ALMI", "ALTO", "AMAG", "AMFG", "AMIN", "AMRT", "ANJT", "ANTM", "APEX", "APIC", "APII", "APLI", "APLN", "ARGO", "ARII", "ARNA", "ARTA", "ARTI", "ARTO", "ASBI", "ASDM", "ASGR", "ASII", "ASJT", "ASMI", "ASRI", "ASRM", "ASSA", "ATIC", "AUTO", "BABP", "BACA", "BAJA", "BALI", "BAPA", "BATA", "BAYU", "BBCA", "BBHI", "BBKP", "BBLD", "BBMD", "BBNI", "BBRI", "BBRM", "BBTN", "BBYB", "BCAP", "BCIC", "BCIP", "BDMN", "BEKS", "BEST", "BFIN", "BGTG", "BHIT", "BIKA", "BIMA", "BINA", "BIPI", "BIPP", "BIRD", "BISI", "BJBR", "BJTM", "BKDP", "BKSL", "BKSW", "BLTA", "BLTZ", "BMAS", "BMRI", "BMSR", "BMTR", "BNBA", "BNBR", "BNGA", "BNII", "BNLI", "BOLT", "BPFI", "BPII", "BRAM", "BRMS", "BRNA", "BRPT", "BSDE", "BSIM", "BUKK", "BULL", "BUMI", "BUVA", "BVIC", "BWPT", "BYAN", "CANI", "CASS", "CEKA", "CENT", "CFIN", "CINT", "CITA", "CLPI", "CMNP", "CMPP", "CNKO", "COWL", "CPIN", "CPRO", "CSAP", "CTBN", "CTRA", "CTTH", "DART", "DEFI", "DEWA", "DGIK", "DILD", "DKFT", "DLTA", "DMAS", "DNAR", "DNET", "DOID", "DPNS", "DSFI", "DSNG", "DSSA", "DUTI", "DVLA", "DYAN", "ECII", "EKAD", "ELSA", "ELTY", "EMDE", "EMTK", "ENRG", "EPMT", "ERAA", "ERTX", "ESSA", "ESTI", "ETWA", "EXCL", "FAST", "FASW", "FISH", "FMII", "FORU", "FPNI", "GAMA", "GDST", "GDYR", "GEMA", "GEMS", "GGRM", "GIAA", "GJTL", "GLOB", "GMTD", "GOLD", "GOLL", "GPRA", "GSMF", "GTBO", "GWSA", "GZCO", "HADE", "HDFA", "HERO", "HEXA", "HITS", "HMSP", "HOME", "HOTL", "HRUM", "IATA", "IBFN", "IBST", "ICBP", "ICON", "IGAR", "IIKP", "IKAI", "IKBI", "IMAS", "IMJS", "IMPC", "INAF", "INAI", "INCI", "INCO", "INDF", "INDR", "INDS", "INDX", "INDY", "INKP", "INPC", "INPP", "INRU", "INTA", "INTD", "INTP", "IPOL", "ISAT", "ISSP", "ITMA", "ITMG", "JAWA", "JECC", "JIHD", "JKON", "JPFA", "JRPT", "JSMR", "JSPT", "JTPE", "KAEF", "KARW", "KBLI", "KBLM", "KBLV", "KBRI", "KDSI", "KIAS", "KICI", "KIJA", "KKGI", "KLBF", "KOBX", "KOIN", "KONI", "KOPI", "KPIG", "KRAS", "KREN", "LAPD", "LCGP", "LEAD", "LINK", "LION", "LMAS", "LMPI", "LMSH", "LPCK", "LPGI", "LPIN", "LPKR", "LPLI", "LPPF", "LPPS", "LRNA", "LSIP", "LTLS", "MAGP", "MAIN", "MAPI", "MAYA", "MBAP", "MBSS", "MBTO", "MCOR", "MDIA", "MDKA", "MDLN", "MDRN", "MEDC", "MEGA", "MERK", "META", "MFMI", "MGNA", "MICE", "MIDI", "MIKA", "MIRA", "MITI", "MKPI", "MLBI", "MLIA", "MLPL", "MLPT", "MMLP", "MNCN", "MPMX", "MPPA", "MRAT", "MREI", "MSKY", "MTDL", "MTFN", "MTLA", "MTSM", "MYOH", "MYOR", "MYTX", "NELY", "NIKL", "NIRO", "NISP", "NOBU", "NRCA", "OCAP", "OKAS", "OMRE", "PADI", "PALM", "PANR", "PANS", "PBRX", "PDES", "PEGE", "PGAS", "PGLI", "PICO", "PJAA", "PKPK", "PLAS", "PLIN", "PNBN", "PNBS", "PNIN", "PNLF", "PNSE", "POLY", "POOL", "PPRO", "PSAB", "PSDN", "PSKT", "PTBA", "PTIS", "PTPP", "PTRO", "PTSN", "PTSP", "PUDP", "PWON", "PYFA", "RAJA", "RALS", "RANC", "RBMS", "RDTX", "RELI", "RICY", "RIGS", "RIMO", "RODA", "ROTI", "RUIS", "SAFE", "SAME", "SCCO", "SCMA", "SCPI", "SDMU", "SDPC", "SDRA", "SGRO", "SHID", "SIDO", "SILO", "SIMA", "SIMP", "SIPD", "SKBM", "SKLT", "SKYB", "SMAR", "SMBR", "SMCB", "SMDM", "SMDR", "SMGR", "SMMA", "SMMT", "SMRA", "SMRU", "SMSM", "SOCI", "SONA", "SPMA", "SQMI", "SRAJ", "SRIL", "SRSN", "SRTG", "SSIA", "SSMS", "SSTM", "STAR", "STTP", "SUGI", "SULI", "SUPR", "TALF", "TARA", "TAXI", "TBIG", "TBLA", "TBMS", "TCID", "TELE", "TFCO", "TGKA", "TIFA", "TINS", "TIRA", "TIRT", "TKIM", "TLKM", "TMAS", "TMPO", "TOBA", "TOTL", "TOTO", "TOWR", "TPIA", "TPMA", "TRAM", "TRIL", "TRIM", "TRIO", "TRIS", "TRST", "TRUS", "TSPC", "ULTJ", "UNIC", "UNIT", "UNSP", "UNTR", "UNVR", "VICO", "VINS", "VIVA", "VOKS", "VRNA", "WAPO", "WEHA", "WICO", "WIIM", "WIKA", "WINS", "WOMF", "WSKT", "WTON", "YPAS", "YULE", "ZBRA", "SHIP", "CASA", "DAYA", "DPUM", "IDPR", "JGLE", "KINO", "MARI", "MKNT", "MTRA", "OASA", "POWR", "INCF", "WSBP", "PBSA", "PRDA", "BOGA", "BRIS", "PORT", "CARS", "MINA", "CLEO", "TAMU", "CSIS", "TGRA", "FIRE", "TOPS", "KMTR", "ARMY", "MAPB", "WOOD", "HRTA", "MABA", "HOKI", "MPOW", "MARK", "NASA", "MDKI", "BELL", "KIOS", "GMFI", "MTWI", "ZINC", "MCAS", "PPRE", "WEGE", "PSSI", "MORA", "DWGL", "PBID", "JMAS", "CAMP", "IPCM", "PCAR", "LCKM", "BOSS", "HELI", "JSKY", "INPS", "GHON", "TDPM", "DFAM", "NICK", "BTPS", "SPTO", "PRIM", "HEAL", "TRUK", "PZZA", "TUGU", "MSIN", "SWAT", "TNCA", "MAPA", "TCPI", "IPCC", "RISE", "BPTR", "POLL", "NFCX", "MGRO", "NUSA", "FILM", "ANDI", "LAND", "MOLI", "PANI", "DIGI", "CITY", "SAPX", "SURE", "HKMU", "MPRO", "DUCK", "GOOD", "SKRN", "YELO", "CAKK", "SATU", "SOSS", "DEAL", "POLA", "DIVA", "LUCK", "URBN", "SOTS", "ZONE", "PEHA", "FOOD", "BEEF", "POLI", "CLAY", "NATO", "JAYA", "COCO", "MTPS", "CPRI", "HRME", "POSA", "JAST", "FITT", "BOLA", "CCSI", "SFAN", "POLU", "KJEN", "KAYU", "ITIC", "PAMG", "IPTV", "BLUE", "ENVY", "EAST", "LIFE", "FUJI", "KOTA", "INOV", "ARKA", "SMKL", "HDIT", "KEEN", "BAPI", "TFAS", "GGRP", "OPMS", "NZIA", "SLIS", "PURE", "IRRA", "DMMX", "SINI", "WOWS", "ESIP", "TEBE", "KEJU", "PSGO", "AGAR", "IFSH", "REAL", "IFII", "PMJS", "UCID", "GLVA", "PGJO", "AMAR", "CSRA", "INDO", "AMOR", "TRIN", "DMND", "PURA", "PTPW", "TAMA", "IKAN", "AYLS", "DADA", "ASPI", "ESTA", "BESS", "AMAN", "CARE", "SAMF", "SBAT", "KBAG", "CBMF", "RONY", "CSMI", "BBSS", "BHAT", "EPAC", "UANG", "PGUN", "SOFA", "PPGL", "TOYS", "SGER", "TRJA", "PNGO", "SCNP", "BBSI", "KMDS", "PURI", "SOHO", "HOMI", "ROCK", "ENZO", "PLAN", "PTDU", "ATAP", "VICI", "PMMP", "WIFI", "FAPA", "DCII", "KETR", "DGNS", "UFOE", "BANK", "WMUU", "EDGE", "UNIQ", "BEBS", "SNLK", "ZYRX", "LFLO", "FIMP", "TAPG", "NPGF", "LUCY", "ADCP", "HOPE"
]
TICKERS = sorted(list(set([f"{t}.JK" if not t.endswith(".JK") else t for t in RAW_TICKERS])))

def scan_ticker(ticker):
    symbol = ticker.replace(".JK", "")
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False, threads=False)
        if df is None or df.empty or len(df) < 30:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        required = ["Open", "High", "Low", "Close", "Volume"]
        clean_df = pd.DataFrame(index=df.index)
        for col in required:
            if col in df.columns:
                s = df[col]
                if isinstance(s, pd.DataFrame):
                    s = s.iloc[:, 0]
                clean_df[col] = pd.to_numeric(s, errors="coerce")
            else:
                return None

        clean_df = clean_df.dropna().sort_index()
        clean_df = clean_df[clean_df["Volume"] >= 0]
        clean_df = clean_df[~clean_df.index.duplicated(keep="last")]

        if len(clean_df) < 20 + 20 + 15:
            return None

        close, high, low, volume = clean_df["Close"], clean_df["High"], clean_df["Low"], clean_df["Volume"]

        hhv_20 = high.rolling(20).max()
        prev_hhv_20 = hhv_20.shift(1)
        prev_prev_hhv_20 = hhv_20.shift(2)
        prev_close = close.shift(1)
        vol_sma_20 = volume.rolling(20).mean()
        ema_20 = close.ewm(span=20, adjust=False).mean()

        high_low_range = (high - low).replace(0, 1)
        clv = ((close - low) - (high - close)) / high_low_range
        top_broker_hist = clv * volume
        
        sum_tb_5 = top_broker_hist.rolling(5).sum()
        sum_tb_15 = top_broker_hist.rolling(15).sum()
        adl = top_broker_hist.cumsum()
        prev_adl = adl.shift(1)

        last = clean_df.iloc[-1]
        
        p_hhv = prev_hhv_20.iloc[-1]
        pp_hhv = prev_prev_hhv_20.iloc[-1]
        p_cls = prev_close.iloc[-1]
        v_sma = vol_sma_20.iloc[-1]
        e_20 = ema_20.iloc[-1]
        tb_5 = sum_tb_5.iloc[-1]
        tb_15 = sum_tb_15.iloc[-1]
        tb_hist = top_broker_hist.iloc[-1]
        curr_adl = adl.iloc[-1]
        p_adl = prev_adl.iloc[-1]

        c_close = float(last["Close"])
        c_vol = float(last["Volume"])
        est_tx = c_close * c_vol

        if est_tx < min_value_rp:
            return None

        # Syarat Screening Breakout
        cond_breakout = c_close > p_hhv
        cond_prev_below = p_cls <= pp_hhv
        cond_volume = c_vol > v_sma
        cond_ema = c_close > e_20
        cond_price = c_close > 70
        cond_tb_5 = tb_5 > 0
        cond_tb_15 = tb_15 > 0
        cond_tb_recent = tb_hist > (tb_5 / 5)
        cond_adl = curr_adl > p_adl

        if not (cond_breakout and cond_prev_below and cond_volume and cond_ema and 
                cond_price and cond_tb_5 and cond_tb_15 and cond_tb_recent and cond_adl):
            return None

        breakout_pct = ((c_close - p_hhv) / p_hhv) * 100

        return {
            "Kode": symbol,
            "Waktu/Candle": pd.Timestamp(clean_df.index[-1]).strftime("%Y-%m-%d %H:%M" if interval != "1d" else "%Y-%m-%d"),
            "Harga Close": round(c_close, 2),
            "Donchian HHV": round(p_hhv, 2),
            "Breakout (%)": round(breakout_pct, 2),
            "Volume": int(c_vol),
            "Est. Nilai Transaksi (Rp)": int(est_tx),
        }
    except Exception:
        return None

# Tombol Eksekusi di Web
if st.button(f"🚀 MULAI SCAN ({interval.upper()})", type="primary"):
    st.info(f"Memindai {len(TICKERS)} emiten pada interval **{interval}**... Mohon tunggu sebentar.")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    completed = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_ticker, t): t for t in TICKERS}
        for future in as_completed(futures):
            completed += 1
            progress_bar.progress(completed / len(TICKERS))
            status_text.text(f"Memproses {completed}/{len(TICKERS)} saham...")
            try:
                res = future.result()
                if res:
                    results.append(res)
            except Exception:
                pass

    status_text.empty()
    progress_bar.empty()

    elapsed = time.time() - start_time
    st.success(f"Pemindaian interval {interval} selesai dalam {elapsed:.1f} detik!")

    if results:
        res_df = pd.DataFrame(results)
        res_df = res_df.sort_values(["Breakout (%)", "Est. Nilai Transaksi (Rp)"], ascending=[False, False]).reset_index(drop=True)
        res_df.insert(0, "Ranking", [f"🥇 Top 1" if i==0 else f"🥈 {i+1}" if i==1 else f"🥉 {i+1}" if i==2 else f"🔥 {i+1}" for i in range(len(res_df))])
        
        st.subheader(f"🎯 Hasil Saham Breakout (Interval: {interval.upper()})")
        st.dataframe(res_df, use_container_width=True)
        
        csv_data = res_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Hasil Scan (CSV)",
            data=csv_data,
            file_name=f"hasil_scanner_breakout_{interval}.csv",
            mime="text/css" if False else "text/csv",
        )
    else:
        st.warning(f"Tidak ada emiten yang memenuhi kriteria breakout pada interval {interval} saat ini.")
else:
    st.write("👈 Pilih interval waktu di sidebar, lalu tekan tombol **MULAI SCAN** untuk memindai pasar.")
