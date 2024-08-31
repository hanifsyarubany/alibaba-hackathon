from http import HTTPStatus
import dashscope
import time

api_key = "sk-b902fd83364046b0b3bc9f49a7bd754c"
dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"
dashscope.api_key = api_key


def generate_completion(system_prompt, user_prompt):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    responses = dashscope.Generation.call(
        "qwen-max",
        messages=messages,
        result_format="message",  # set the result to be "message"  format.
        stream=True,  # set streaming output
        incremental_output=True,  # get streaming output incrementally
    )
    text = ""
    for response in responses:
        if response.status_code == HTTPStatus.OK:
            text += response.output.choices[0]["message"]["content"]
        else:
            print(
                "Request id: %s, Status code: %s, error code: %s, error message: %s"
                % (
                    response.request_id,
                    response.status_code,
                    response.code,
                    response.message,
                )
            )

    return text


class PromptReplacer:
    def __init__(self, template):
        self.template = template

    def replace_entities(self, replacements):
        updated_template = self.template
        for key, value in replacements.items():
            updated_template = updated_template.replace(key, value)
        return updated_template


# PROMPT TEMPLATE: for generating summary
_system_prompt_overview_1st = """
You need to tell the user, what's wrong with his/her business. 
Given data comprises of his specific business, location, and his complaint in bahasa (Indonesian language).
Based on the information provided, please response in bahasa to answer why his business is declining.
please response in as concise as possible with a maximum 3 sentences. 
"""
_user_prompt_overview_1st = """
### Business: <<nama_usaha>>
### Location: <<lokasi_usaha>>
### Complaint: <<hambatan_utama>>
### ANSWER: 
"""
# PROMPT TEMPLATE: for generating suggestion
_system_prompt_overview_2nd = """
You need to tell the user, what's wrong with his/her business. 
Given data comprises of his specific business, location, and his complaint in bahasa (Indonesian language).
Based on the information provided, please response in bahasa to answer what he should do. Give him a quick suggestion like expanding and scaling the market or something.
please response in as concise as possible with a maximum 2 sentences. 
"""
_user_prompt_overview_2nd = """
### Business: <<nama_usaha>>
### Location: <<lokasi_usaha>>
### Complaint: <<hambatan_utama>>
### ANSWER: 
"""


def overview_builder(session_id, payload_form):
    # generate summary
    summary = generate_completion(
        _system_prompt_overview_1st,
        PromptReplacer(_user_prompt_overview_1st).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<lokasi_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "lokasi_usaha"
                ],
                "<<hambatan_utama>>": payload_form["informasi_keluhan_atau_hambatan"][
                    "hambatan_utama_yang_dihadapi"
                ],
            }
        ),
    )
    time.sleep(1)
    # generate suggestion
    suggestion = generate_completion(
        _system_prompt_overview_2nd,
        PromptReplacer(_user_prompt_overview_2nd).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<lokasi_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "lokasi_usaha"
                ],
                "<<hambatan_utama>>": payload_form["informasi_keluhan_atau_hambatan"][
                    "hambatan_utama_yang_dihadapi"
                ],
            }
        ),
    )
    # generate payload
    payload_output = {
        "session_id": session_id,
        "module": "overview_builder",
        "summary": summary,
        "suggestion": suggestion,
    }
    # return output
    time.sleep(2)
    return payload_output


# PROMPT TEMPLATE: for generating strength potential
_system_prompt_expansion_1st = """
Given information of the small medium business in bahasa (indonesian language). 
Based on the information you need to assess 6 metrics:
Production capacity, Business size, Quality standard, Logistic networks, Cultural value, Futuristic value. 

If the product contain art or creativity or furniture use, then you should give very high score in cultural value and futuristic value.

Please assess those 6 metrics and answer in a scale of 0-100. 
Please format your answer like this example:
50|||20|||33|||55|||45|||70
"""
_user_prompt_expansion_1st = """
### Business: <<nama_usaha>>
### Product: <<jenis_produk>>
### Product Quality Standard: <<standar_kualitas_produk>>
### Business Scale: <<skala_usaha>>
### Target Market: <<target_pasar>>
### Marketing Outreach: <<jangkauan_pemasaran>>
### Current Sales Channels: <<saluran_penjualan_saat_ini>>
### ANSWER: 
"""


# PROMPT TEMPLATE: for generating insight
_system_prompt_expansion_2nd = """
Given an information in bahasa (indonesian language) comprises of business and product details as well as a radar chart information in a scale of 0-100. 

Please give a quick insight referring to the radar chart. and also in the insight, please give what is the probability to grow. 
Please response in bahasa in a maximum of 2 sentences
"""
_user_prompt_expansion_2nd = """
### Business: <<nama_usaha>>
### Product: <<jenis_produk>>
### Radar Chart:
Kapasitas produksi: <<kapasitas_produksi>>
Ukuran Bisnis: <<ukuran_bisnis>>
Standar Kualitas: <<standar_kualitas>>
Jaringan Logistik: <<jaringan_logistik>>
Nilai Budaya: <<nilai_budaya>>
Nilai Futuristik: <<nilai_futuristik>>

### ANSWER: 
"""

# PROMPT TEMPLATE: for generating maket size estimation small
_system_prompt_expansion_3rd = """
Given an information in bahasa (indonesian language) comprises of business and product details.
Other than that, there is a specific location of his/her business in Indonesia (rural areas).
Firstly, based on the location of his/her business, you need to search the near location, at least 4 (terdiri dari daerah kecamatan dan perkotaan), 
that has high potential demand of his/her business and product.

After that you need to calculate the market size potential in IDR in billion (or milyar in bahasa).

Please follow this example format to answer:

# Example 1:
Kecamatan Weru---10.8|||Kecamatan Cisalak---8.8|||Kecamatn Coblong---12.5|||Kota Cirebon---86.5
"""
_user_prompt_expansion_3rd = """
### Business: <<nama_usaha>>
### Product: <<jenis_produk>>
### Location: <<lokasi_usaha>>
### ANSWER: 
"""

# PROMPT TEMPLATE: for generating maket size estimation big
_system_prompt_expansion_4th = """
Given an information in bahasa (indonesian language) comprises of business and product details.
His/her business operates in indonesia.
Firstly, you need to search the location of outside indonesia (overseas countries), at least 4 countries, 
that has high potential demand of his/her business and product.

After that you need to calculate the market size potential in IDR in billion (or milyar in bahasa).

Please follow this example format to answer:

# Example 1:
Peru---10.8|||Malaysia---8.8|||Netherland---12.5|||French---86.5
"""
_user_prompt_expansion_4th = """
### Business: <<nama_usaha>>
### Product: <<jenis_produk>>
### ANSWER: 
"""

# PROMPT TEMPLATE: for generating maket size estimation small insight
_system_prompt_expansion_5th = """
Given an information in bahasa (indonesian language) comprises of business and product details of the users as well as a bar chart containing value of market size in Billion IDR (billion rupiah) 

Please give a quick insight referring to the bar chart. 
Firtly, you just need to take a look only at the bar chart which has the biggest value. (only 1 location)
After that, you need to give a quick insight on why do you think that location has very high demand in terms of the users' business product.

Please response in bahasa in a maximum of 2 sentences
"""
_user_prompt_expansion_5th = """
### Business: <<nama_usaha>>
### Product: <<jenis_produk>>
### Bar Chart:
<<bar_chart>>
### ANSWER: 
"""

# PROMPT TEMPLATE: for generating maket size estimation big insight
_system_prompt_expansion_6th = """
Given an information in bahasa (indonesian language) comprises of business and product details of the users as well as a bar chart containing value of market size in Billion IDR (billion rupiah) 

Please give a quick insight referring to the bar chart. 
Firtly, you just need to take a look only at the bar chart which has the biggest value. (only 1 location of country)
After that, you need to give a quick insight on why do you think that location has very high demand in terms of the users' business product.

Please response in bahasa in a maximum of 2 sentences
"""
_user_prompt_expansion_6th = """
### Business: <<nama_usaha>>
### Product: <<jenis_produk>>
### Bar Chart:
<<bar_chart>>
### ANSWER: 
"""


def market_expansion_opportunities(session_id, payload_form):
    # generate strength potential
    strength_potential = generate_completion(
        _system_prompt_expansion_1st,
        PromptReplacer(_user_prompt_expansion_1st).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<standar_kualitas_produk>>": payload_form["informasi_bisnis_dasar"][
                    "standar_kualitas_produk"
                ],
                "<<skala_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "skala_usaha"
                ],
                "<<target_pasar>>": payload_form["informasi_pasar_dan_penjualan"][
                    "target_pasar"
                ],
                "<<jangkauan_pemasaran>>": payload_form[
                    "informasi_pasar_dan_penjualan"
                ]["jangkauan_pemasaran"],
                "<<saluran_penjualan_saat_ini>>": payload_form[
                    "informasi_pasar_dan_penjualan"
                ]["saluran_penjualan_saat_ini"],
            }
        ),
    )
    # create dict_chart
    arr_strength = strength_potential.split("|||")
    dict_chart = {
        "kapasitas_produksi": arr_strength[0],
        "ukuran_bisnis": arr_strength[1],
        "standar_kualitas": arr_strength[2],
        "jaringan_logistik": arr_strength[3],
        "nilai_budaya": arr_strength[4],
        "nilai_futuristik": arr_strength[5],
    }
    # generate insight
    insight_strength_potential = generate_completion(
        _system_prompt_expansion_2nd,
        PromptReplacer(_user_prompt_expansion_2nd).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<kapasitas_produksi>>": dict_chart["kapasitas_produksi"],
                "<<ukuran_bisnis>>": dict_chart["ukuran_bisnis"],
                "<<standar_kualitas>>": dict_chart["standar_kualitas"],
                "<<jaringan_logistik>>": dict_chart["jaringan_logistik"],
                "<<nilai_budaya>>": dict_chart["nilai_budaya"],
                "<<nilai_futuristik>>": dict_chart["nilai_futuristik"],
            }
        ),
    )
    # generate market size small
    market_size_small = generate_completion(
        _system_prompt_expansion_3rd,
        PromptReplacer(_user_prompt_expansion_3rd).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<lokasi_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "lokasi_usaha"
                ],
            }
        ),
    )
    dict_market_size_small = {}
    for i in market_size_small.split("|||"):
        key = i.split("---")[0]
        val = i.split("---")[1]
        dict_market_size_small[key] = val
    # generate market size small insight
    insight_small = generate_completion(
        _system_prompt_expansion_5th,
        PromptReplacer(_user_prompt_expansion_5th).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<bar_chart>>": str(dict_market_size_small),
            }
        ),
    )
    # generate market size big
    market_size_big = generate_completion(
        _system_prompt_expansion_4th,
        PromptReplacer(_user_prompt_expansion_4th).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<lokasi_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "lokasi_usaha"
                ],
            }
        ),
    )
    dict_market_size_big = {}
    for i in market_size_big.split("|||"):
        key = i.split("---")[0]
        val = i.split("---")[1]
        dict_market_size_big[key] = val
    # generate market size big insight
    insight_big = generate_completion(
        _system_prompt_expansion_6th,
        PromptReplacer(_user_prompt_expansion_6th).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<bar_chart>>": str(dict_market_size_big),
            }
        ),
    )
    # generate payload
    payload_output = {
        "session_id": session_id,
        "module": "market expansion opportunities",
        "strength_potential_chart": dict_chart,
        "insight_strength_potential": insight_strength_potential,
        "market_size_estimation_local": dict_market_size_small,
        "market_size_estimation_local_insight": insight_small,
        "market_size_estimation_international": dict_market_size_big,
        "market_size_estimation_international_insight": insight_big,
    }
    # return output
    time.sleep(2)
    return payload_output


# PROMPT TEMPLATE: for generating diferensiasi produk
_system_prompt_gtm_diferensiasi = """
Given an information in bahasa (indonesian language) comprises of the details of his business. 
He lives in rural areas and somehow he want to expand his business to thrive and compete. 
Please tell him how to make his business product unique (poduct differentiation).
Please use `kamu` when referring to the user.
Please response in a maximum of 2 sentences in bahasa (indonesian language)
"""
_system_prompt_gtm = """
### Business: <<nama_usaha>>
### Product: <<jenis_produk>>
### Business Scale: <<skala_usaha>>
### Customer Profile: <<profil_pelanggan>>
### ANSWER: 
"""
# PROMPT TEMPLATE: for generating strategi penetapan harga
_system_prompt_gtm_strategi = """
Given an information in bahasa (indonesian language) comprises of the details of his business. 
He lives in rural areas and somehow he want to expand his business to thrive and compete. 
Please tell him about the pricing strategy that he can implement.
Please use `kamu` when referring to the user.
Please response in a maximum of 2 sentences in bahasa (indonesian language)
"""
# PROMPT TEMPLATE: for generating saluran distibusi
_system_prompt_gtm_saluran = """
Given an information in bahasa (indonesian language) comprises of the details of his business. 
He lives in rural areas and somehow he want to expand his business to thrive and compete. 
Please tell him about the distribution channels (saluran distribusi) that he can implement (ex. using a combination of online e-commerce and offline).
Please use `kamu` when referring to the user.
Please response in a maximum of 2 sentences in bahasa (indonesian language)
"""
# PROMPT TEMPLATE: for generating pricing model
_system_prompt_gtm_pricing = """
Given an information in bahasa (indonesian language) comprises of the details of his business. 
He lives in rural areas and somehow he want to expand his business to thrive and compete. 
Please tell him about the value-based pricing model example that he can implement.
Please set the price example. 
Please use `kamu` when referring to the user.
Please response in a maximum of 2 sentences in bahasa (indonesian language)
"""
# PROMPT TEMPLATE: for milestone revenue
_system_prompt_gtm_revenue = """
Given an information in bahasa (indonesian language) comprises of the details of his business. 
He lives in rural areas and somehow he want to expand his business to thrive and compete.
He want to scale up his business to penetrate national and international market.  

Based on the information provided, 
Firstly, you need to calculate the potential revenue that he can capture in million IDR (juta rupiah) in 5 years.
The first year should be the lowest, and it will grow exponentially. 

Please do calculation and answer in million IDR value

You are only allowed to provide the answer using the format like this example:
500|||1200|||2500|||5250|||10000
"""
# PROMPT TEMPLATE: for milestone formatting
_system_prompt_gtm_formatting = """
Given a text string. You need to find a pattern like this example:
`500|||1200|||2500|||5250|||10000`

Please find return that pattern-like string in your response
"""
_user_prompt_gtm_formatting = """
### TEXT: <<text>>
### ANSWER: """


def gtm_strategy(session_id, payload_form):
    # Generate diferrensiasi
    diferensiasi_produk = generate_completion(
        _system_prompt_gtm_diferensiasi,
        PromptReplacer(_system_prompt_gtm).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<skala_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "skala_usaha"
                ],
                "<<profil_pelanggan>>": payload_form["informasi_pasar_dan_penjualan"][
                    "profil_pelanggan"
                ],
            }
        ),
    )
    # Generate strategi
    strategi_penetapan_harga = generate_completion(
        _system_prompt_gtm_strategi,
        PromptReplacer(_system_prompt_gtm).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<skala_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "skala_usaha"
                ],
                "<<profil_pelanggan>>": payload_form["informasi_pasar_dan_penjualan"][
                    "profil_pelanggan"
                ],
            }
        ),
    )
    # Generate saluran
    saluran_distribusi = generate_completion(
        _system_prompt_gtm_saluran,
        PromptReplacer(_system_prompt_gtm).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<skala_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "skala_usaha"
                ],
                "<<profil_pelanggan>>": payload_form["informasi_pasar_dan_penjualan"][
                    "profil_pelanggan"
                ],
            }
        ),
    )
    # Generate marketing
    marketing_channel = "E-commerce platforms, Social media commerce, retail partnerships, pop-up shops and events, direct-to-customer channels"
    # Generate pricing model
    jenis_pricing_model = "Value-Based Pricing"
    contoh_harga = generate_completion(
        _system_prompt_gtm_pricing,
        PromptReplacer(_system_prompt_gtm).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<skala_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "skala_usaha"
                ],
                "<<profil_pelanggan>>": payload_form["informasi_pasar_dan_penjualan"][
                    "profil_pelanggan"
                ],
            }
        ),
    )
    # Generate Milestone
    milestone = {
        "1": (
            "Foundation and Initial Market Penetration",
            "Penetrasi pasar lokal melalui e-commerce dan media sosial, partisipasi dalam pameran lokal",
        ),
        "2": (
            "Brand Building and Market Expansion",
            "Ekspansi ke kota-kota besar lainnya di Indonesia, memulai penetrasi pasar internasional secara terbatas (China dan AS)",
        ),
        "3": (
            "Scaling Operations and International Expansion",
            "Meningkatkan volume ekspor dan menjual di platform internasional, mengikuti pameran dagang internasional",
        ),
        "4": (
            "Market Leadership and Diversification",
            "Diversifikasi produk dan memperluas distribusi internasional, memperkuat posisi di segmen premium",
        ),
        "5": (
            "Consolidation and Innovation",
            "Konsolidasi dan inovasi produk, memperkuat brand positioning sebagai pemimpin pasar global di furnitur rotan tradisional.",
        ),
    }
    # Generate market size timeline
    revenue = generate_completion(
        _system_prompt_gtm_revenue,
        PromptReplacer(_system_prompt_gtm).replace_entities(
            {
                "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
                "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"][
                    "jenis_produk"
                ],
                "<<skala_usaha>>": payload_form["informasi_bisnis_dasar"][
                    "skala_usaha"
                ],
                "<<profil_pelanggan>>": payload_form["informasi_pasar_dan_penjualan"][
                    "profil_pelanggan"
                ],
            }
        ),
    )
    revenue_string = generate_completion(
        _system_prompt_gtm_formatting,
        _user_prompt_gtm_formatting.replace("<<text>>", revenue),
    )
    revenue_arr = revenue_string.split("\n")[-1].split("|||")
    market_size_timeline = {
        "1": revenue_arr[0],
        "2": revenue_arr[1],
        "3": revenue_arr[2],
        "4": revenue_arr[3],
        "5": revenue_arr[4],
    }
    # generate payload
    payload_output = {
        "session_id": session_id,
        "module": "go-to-market strategy",
        "strategy_panel": {
            "diferensiasi_produk": diferensiasi_produk,
            "strategi_penetapan_harga": strategi_penetapan_harga,
            "saluran_distribusi": saluran_distribusi,
            "marketing_channel": marketing_channel,
        },
        "pricing_model_panel": {
            "jenis_pricing_model": jenis_pricing_model,
            "contoh_harga": contoh_harga,
        },
        "milestone": milestone,
        "market_size_timeline": market_size_timeline,
    }
    # return output
    time.sleep(2)
    return payload_output

# PROMPT TEMPLATE: for generating funding calculation
system_prompt_fnc_1st="""
Diketahui bahwa user sedang mengembangkan bisnis sebagai berikut.
### Bisnis: <<nama usaha>>
### Produk: <<jenis_produk>>

Bisnisnya dia beroperasi di daerah  <<lokasi_usaha>>.

Nah, sekarang, dia hendak melakukan ekspansi dari daerahnya dia hingga ke perrkotaan dan juga ke skala intenasional. 
Coba, menurutmu, kira-kira dia harus dapet funding seberapa besar. 

Tolong beri respon nominal rupiahnya saja dalam miliyar rupiah.

Contoh Jawaban #1:
IDR 5,45 M
"""
user_prompt_fnc = """
### Jawab: """

# PROMPT TEMPLATE: for generating how_to_get_fund
system_prompt_fnc_2nd="""
Diketahui bahwa user sedang mengembangkan bisnis sebagai berikut.
### Bisnis: <<nama usaha>>
### Produk: <<jenis_produk>>

Bisnisnya dia beroperasi di daerah  <<lokasi_usaha>>.

Nah, sekarang, dia hendak melakukan ekspansi dari daerahnya dia hingga ke perkotaan dan juga ke skala intenasional. 
Coba, menurutmu, kira kira di daerah terdekatnya, di desanya itu, dimulai dari titik daerahnya, bagaimana caranya dia dapet funding.

Kamu harus batasi responsmu dalam maksimal 3 kalimat saja.
Ketika kamu jawab ke user, refer user pakai kata 'kamu' saja. 
"""

# PROMPT TEMPLATE: for generating how_to_get_fund
system_prompt_fnc_3rd = """
Diketahui bahwa user sedang mengembangkan bisnis sebagai berikut.
### Bisnis: <<nama usaha>>
### Produk: <<jenis_produk>>

Bisnisnya dia beroperasi di daerah  <<lokasi_usaha>>.

Nah, sekarang, dia hendak melakukan ekspansi dari daerahnya dia hingga ke perkotaan dan juga ke skala intenasional. 
Tolong beri tahu, komunitas komunitas apa saja di daerah terdekatnya untuk membantu dia berkembang sebagai networking, mulai dari daerah lokasi usahanya. 

Kamu harus batasi responsmu dalam maksimal 3 kalimat saja.
Ketika kamu jawab ke user, refer user pakai kata 'kamu' saja. 
"""


def funding_community(business_id, payload_form):
    # Generate funding
    system_prompt_fnc_1st_x = PromptReplacer(system_prompt_fnc_1st).replace_entities({
        "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
        "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"]["jenis_produk"],
        "<<lokasi_usaha>>": payload_form["informasi_bisnis_dasar"]["lokasi_usaha"],
    })
    funding = generate_completion(system_prompt_fnc_1st_x, user_prompt_fnc)

    # Generate how to get fund
    system_prompt_fnc_2nd_x = PromptReplacer(system_prompt_fnc_2nd).replace_entities({
        "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
        "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"]["jenis_produk"],
        "<<lokasi_usaha>>": payload_form["informasi_bisnis_dasar"]["lokasi_usaha"],
    })
    how_to_get_fund = generate_completion(system_prompt_fnc_2nd_x, user_prompt_fnc)

    # Generate community
    system_prompt_fnc_3rd_x = PromptReplacer(system_prompt_fnc_3rd).replace_entities({
        "<<nama_usaha>>": payload_form["informasi_bisnis_dasar"]["nama_usaha"],
        "<<jenis_produk>>": payload_form["informasi_bisnis_dasar"]["jenis_produk"],
        "<<lokasi_usaha>>": payload_form["informasi_bisnis_dasar"]["lokasi_usaha"],
    })
    community = generate_completion(system_prompt_fnc_3rd_x, user_prompt_fnc)

    # generate payload
    payload_output = {
        "business_id": business_id,
        "module": "funding-community",
        "funding": funding,
        "how_to_get_fund": how_to_get_fund,
        "community": community
    }
    # return output
    time.sleep(5)
    return payload_output
