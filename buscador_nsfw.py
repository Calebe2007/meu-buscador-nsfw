import streamlit as st
import requests

st.set_page_config(page_title="Buscador NSFW Melhor que Gelbooru", layout="wide", page_icon="🔥", initial_sidebar_state="expanded")

# CSS melhorado (mais parecido com site booru, hover forte, clean)
st.markdown("""
    <style>
    .stApp { background-color: #111; color: #eee; }
    .image-card { 
        background: #181818; 
        border-radius: 12px; 
        padding: 12px; 
        margin: 12px 0; 
        box-shadow: 0 6px 12px rgba(0,0,0,0.5); 
        transition: all 0.25s ease; 
        overflow: hidden;
    }
    .image-card:hover { 
        transform: translateY(-5px) scale(1.03); 
        box-shadow: 0 12px 24px rgba(255,0,120,0.4); 
        border: 1px solid #ff0077;
    }
    .stButton > button { 
        background: linear-gradient(90deg, #ff0066, #cc0066); 
        color: white; 
        border: none; 
        border-radius: 20px; 
        padding: 10px 20px; 
        font-weight: bold;
    }
    .stTextInput > div > div > input { 
        background: #222; 
        color: #fff; 
        border: 1px solid #444; 
        border-radius: 8px;
    }
    .suggestion-btn { 
        background: #222 !important; 
        color: #eee !important; 
        border: 1px solid #444 !important; 
        border-radius: 20px !important; 
        margin: 4px !important;
    }
    .suggestion-btn:hover { background: #333 !important; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar minimalista
with st.sidebar:
    st.title("Buscador NSFW Superior 🔥")
    api_key = st.text_input("Gelbooru API Key", type="password", value="c084ca0acb8abac134504acd4b0fde0e3bca96df5898cb1869abe29871c5f554991d072adef7c95a41c034b5257330aef9ee0488151a05e20d1fcd39ac88403e")
    user_id = st.text_input("Gelbooru User ID", value="1910925")
    
    tag_input = st.text_input(
        "Digite tags",
        placeholder="Ex: yoru, nami, hinata...",
        help="Autocomplete 100% igual ao site Gelbooru — sugestões reais e infinitas direto da API."
    )
    
    limit = st.slider("Imagens por busca", 6, 60, 24, step=6)

# Função sugestões (puro API, como o site)
@st.cache_data(ttl=180)  # cache curto pra sempre fresco
def get_gelbooru_suggestions(pattern, api_key, user_id):
    if len(pattern) < 1:
        return []
    params = {
        "page": "dapi",
        "s": "tag",
        "q": "autocomplete",
        "json": 1,
        "tag_pattern": pattern + "*",
        "api_key": api_key,
        "user_id": user_id,
        "limit": 30  # mais sugestões que o site padrão
    }
    try:
        r = requests.get("https://gelbooru.com/index.php", params=params, timeout=4)
        r.raise_for_status()
        data = r.json()
        return [item['tag'] for item in data if 'tag' in item][:30]
    except requests.exceptions.HTTPError as e:
        if r.status_code in [401, 403]:
            st.error(f"Key/ID inválida (erro {r.status_code}). Gere nova no perfil com VPN ligada.")
        else:
            st.error(f"Erro API: {r.status_code} - {e}")
        return []
    except Exception as e:
        st.error(f"Erro conexão/API: {e}. Use VPN se bloqueado no BR.")
        return []

# Área principal clean
st.title("Buscador NSFW Melhor que o Site 🍑")
st.markdown("Autocomplete **exatamente** como no Gelbooru oficial — digite e veja sugestões reais/infinita do banco deles. Clique pra adicionar.")

suggestions = []
if tag_input:
    suggestions = get_gelbooru_suggestions(tag_input.strip(), api_key, user_id)
    
    if suggestions:
        st.markdown("**Sugestões reais do Gelbooru (clique pra adicionar):**")
        cols = st.columns(6)  # mais colunas pra ficar como dropdown amplo
        for i, sug in enumerate(suggestions):
            with cols[i % 6]:
                if st.button(sug, key=f"sug_{i}_{tag_input}", use_container_width=True, help=sug):
                    current = st.session_state.get("final_tags", "")
                    if current and not current.endswith(" "):
                        current += " "
                    st.session_state["final_tags"] = current + sug + " "
                    st.rerun()
    else:
        st.caption("Digite mais (ex: 'yoru' pra yoruichi, 'nami' pra One Piece) — sugestões vêm direto do site.")

# Campo final
final_tags = st.text_input("Tags finais (edite livremente):", value=st.session_state.get("final_tags", tag_input), key="final_tags")

if st.button("Buscar Agora 🔥", type="primary", use_container_width=True):
    if not final_tags.strip():
        st.error("Digite tags!")
    elif not api_key or not user_id:
        st.error("Preencha API Key e User ID no sidebar!")
    else:
        with st.spinner("Carregando imagens reais do Gelbooru..."):
            params = {
                "page": "dapi",
                "s": "post",
                "q": "index",
                "json": 1,
                "limit": limit,
                "tags": final_tags.strip().replace(" ", "+"),
                "api_key": api_key,
                "user_id": user_id
            }
            try:
                response = requests.get("https://gelbooru.com/index.php", params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                posts = data.get("post", [])
                if not isinstance(posts, list):
                    posts = [posts] if posts else []

                if not posts:
                    st.warning("Nenhuma imagem encontrada. Tente remover filtros ou tags mais gerais.")
                else:
                    st.success(f"Encontradas {len(posts)} imagens reais! 🔥")
                    cols = st.columns(3)
                    for idx, post in enumerate(posts):
                        file_url = post.get("file_url") or post.get("sample_url")
                        if file_url:
                            preview = post.get("preview_url") or file_url
                            score = post.get("score", "N/A")
                            tags_short = post.get("tags", "")[:100] + "..." if len(post.get("tags", "")) > 100 else post.get("tags", "")
                            with cols[idx % 3]:
                                st.markdown('<div class="image-card">', unsafe_allow_html=True)
                                st.image(preview, use_column_width=True)
                                st.caption(f"**Score:** {score} | Tags: {tags_short}")
                                st.markdown(f"[Ver full size]({file_url})", unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro na busca: {e}. Key/ID inválida? Gere nova no perfil.")

st.markdown("---")
st.caption("Autocomplete 100% real do Gelbooru (milhões de tags infinitas do site). Sem lista fixa, sem fallback — puro como o oficial, mas melhor visual e fluidez.")