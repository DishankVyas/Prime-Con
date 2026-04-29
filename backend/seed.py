import random
from datetime import date, timedelta
from faker import Faker
from database import get_session, VBAK, VBAP, BKPF, BSEG, EKKO, EKPO, MSEG, AUFK, CDHDR, CDPOS
from sqlalchemy import select, func

fake = Faker()
Faker.seed(42)
random.seed(42)

def seed_data():
    with get_session() as session:
        if session.execute(select(VBAK).limit(1)).scalar_one_or_none() is not None:
            print("Database already contains data. Skipping seed.")
            return

        customers = [f"KU-{10000+i}" for i in range(500)]
        vendors = [f"LI-{20000+i}" for i in range(300)]
        materials = [f"MAT-A{str(i+1).zfill(3)}" for i in range(200)]
        plants = [f"PLANT-{str(i+1).zfill(3)}" for i in range(10)]

        start_date = date(2023, 1, 1)
        end_date = date(2025, 4, 30)

        def random_date():
            return fake.date_between(start_date=start_date, end_date=end_date)

        # 1. VBAK (2000) & VBAP (8000)
        print("Seeding VBAK/VBAP: 0/2000 rows")
        vbak_list = []
        vbap_list = []
        for i in range(2000):
            vbeln = f"V-{str(i+1).zfill(8)}"
            erdat = random_date()
            netwr = round(random.uniform(500, 500000), 2)
            auart = "RE" if random.random() < 0.08 else "TA"
            vbak = VBAK(
                vbeln=vbeln, erdat=erdat, kunnr=random.choice(customers),
                netwr=netwr, waerk="EUR", vkorg="1000", vtweg="10",
                spart="00", auart=auart, vbtyp="C"
            )
            vbak_list.append(vbak)
            
            num_items = 4 # 8000 / 2000
            for j in range(num_items):
                posnr = str((j+1)*10).zfill(6)
                netpr = round(netwr / num_items, 2)
                vbap = VBAP(
                    vbeln=vbeln, posnr=posnr, matnr=random.choice(materials),
                    arktx=fake.word()[:40], kwmeng=random.randint(1, 100),
                    meins="EA", netpr=netpr, werks=random.choice(plants), lgort="0001"
                )
                vbap_list.append(vbap)
                
            if (i+1) % 500 == 0:
                print(f"Seeding VBAK: {i+1}/2000 rows")

        session.add_all(vbak_list)
        session.add_all(vbap_list)
        session.commit()

        # 2. BKPF (3000) & BSEG (9000)
        print("Seeding BKPF/BSEG: 0/3000 rows")
        bkpf_list = []
        bseg_list = []
        today = date.today()
        for i in range(3000):
            belnr = f"B-{str(i+1).zfill(8)}"
            bldat = random_date()
            
            # 10% overdue without clearing
            if random.random() < 0.10:
                budat = bldat - timedelta(days=random.randint(46, 100))
            else:
                budat = bldat + timedelta(days=random.randint(0, 30))
                
            bkpf = BKPF(
                bukrs="1000", belnr=belnr, gjahr=bldat.year,
                blart="KR", bldat=bldat, budat=budat,
                xblnr=fake.word()[:16], bktxt=fake.sentence()[:25], waers="EUR",
                usnam=fake.user_name()[:12]
            )
            bkpf_list.append(bkpf)

            num_items = 3 # 9000 / 3000
            for j in range(num_items):
                buzei = str(j+1).zfill(3)
                dmbtr = round(random.uniform(100, 10000), 2)
                bseg = BSEG(
                    bukrs="1000", belnr=belnr, gjahr=bldat.year, buzei=buzei,
                    hkont=str(random.randint(100000, 999999)), shkzg=random.choice(["S", "H"]),
                    dmbtr=dmbtr, wrbtr=dmbtr, kostl="K-1000", prctr="P-2000",
                    mwskz="V1", zterm="0001"
                )
                bseg_list.append(bseg)
            
            if (i+1) % 500 == 0:
                print(f"Seeding BKPF: {i+1}/3000 rows")

        session.add_all(bkpf_list)
        session.add_all(bseg_list)
        session.commit()
        
        # 3. EKKO (1500) & EKPO (4500)
        print("Seeding EKKO/EKPO: 0/1500 rows")
        ekko_list = []
        ekpo_list = []
        for i in range(1500):
            ebeln = f"E-{str(i+1).zfill(8)}"
            ekko = EKKO(
                ebeln=ebeln, bukrs="1000", bsart="NB", lifnr=random.choice(vendors),
                ekgrp="001", bedat=random_date(), waers="EUR", zterm="0001", inco1="EXW"
            )
            ekko_list.append(ekko)

            num_items = 3 # 4500 / 1500
            for j in range(num_items):
                ebelp = str((j+1)*10).zfill(5)
                ekpo = EKPO(
                    ebeln=ebeln, ebelp=ebelp, matnr=random.choice(materials),
                    txz01=fake.word()[:40], menge=random.randint(1, 100), meins="EA",
                    netpr=round(random.uniform(10, 5000), 2), peinh=1.0, werks=random.choice(plants),
                    eindt=random_date(), knttp=""
                )
                ekpo_list.append(ekpo)
                
            if (i+1) % 500 == 0:
                print(f"Seeding EKKO: {i+1}/1500 rows")

        session.add_all(ekko_list)
        session.add_all(ekpo_list)
        session.commit()

        # 4. MSEG (5000)
        print("Seeding MSEG: 0/5000 rows")
        mseg_list = []
        for i in range(5000):
            mseg = MSEG(
                mblnr=f"M-{str(i+1).zfill(8)}", mjahr=random_date().year, zeile="0001",
                bwart="101", matnr=random.choice(materials), werks=random.choice(plants),
                lgort="0001", menge=random.randint(1, 100), meins="EA",
                dmbtr=round(random.uniform(100, 5000), 2), kostl="K-1000", aufnr="",
                ebeln="", ebelp=""
            )
            mseg_list.append(mseg)
            if (i+1) % 500 == 0:
                print(f"Seeding MSEG: {i+1}/5000 rows")

        session.add_all(mseg_list)
        session.commit()

        # 5. AUFK (800)
        print("Seeding AUFK: 0/800 rows")
        aufk_list = []
        for i in range(800):
            gstrs = random_date()
            gltrs = gstrs + timedelta(days=random.randint(1, 10))
            gstri = gstrs
            
            # 15% late
            if random.random() < 0.15:
                getri = gltrs + timedelta(days=random.randint(1, 5))
            else:
                getri = gltrs

            aufk = AUFK(
                aufnr=f"A-{str(i+1).zfill(10)}", auart="PP01", erdat=gstrs,
                matnr=random.choice(materials), werks=random.choice(plants),
                gamng=random.randint(10, 1000), gmein="EA",
                gstrs=gstrs, gltrs=gltrs, gstri=gstri, getri=getri,
                igmng=random.randint(10, 1000), aueru=""
            )
            aufk_list.append(aufk)
            if (i+1) % 500 == 0:
                print(f"Seeding AUFK: {i+1}/800 rows")
        print(f"Seeding AUFK: 800/800 rows")
        session.add_all(aufk_list)
        session.commit()

        # 6. CDHDR (10000) & CDPOS (25000)
        print("Seeding CDHDR/CDPOS: 0/10000 rows")
        cdhdr_list = []
        cdpos_list = []
        tcode_map = {
            "VERKBELEG": ["VA01","VA02","VL01N","VF01","FBZ5"],
            "EINKBELEG": ["ME21N","ME22N","MIGO","MIRO","F110"],
            "production": ["CO01","CO02","CO11N","CO15"]
        }
        for i in range(10000):
            changenr = f"C-{str(i+1).zfill(8)}"
            objectclas = random.choice(list(tcode_map.keys()))
            tcode = random.choice(tcode_map[objectclas])
            cdhdr = CDHDR(
                changenr=changenr, objectclas=objectclas, objectid=f"OBJ-{i}",
                udate=random_date(), utime=fake.time_object(),
                username=fake.user_name()[:12], tcode=tcode
            )
            cdhdr_list.append(cdhdr)

            num_items = random.choice([2, 3]) # 25000 / 10000 is avg 2.5
            for j in range(num_items):
                cdpos = CDPOS(
                    changenr=changenr, tabname="TAB", fname=f"FIELD-{j}",
                    chngind="U", value_new=fake.word()[:20], value_old=fake.word()[:20]
                )
                cdpos_list.append(cdpos)

            if (i+1) % 500 == 0:
                print(f"Seeding CDHDR: {i+1}/10000 rows")

        session.add_all(cdhdr_list)
        session.add_all(cdpos_list)
        session.commit()

if __name__ == "__main__":
    seed_data()
