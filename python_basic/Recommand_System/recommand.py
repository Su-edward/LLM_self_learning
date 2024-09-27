#隱式協同過濾（Implicit Collaborative Filtering）技術
#透過Alternating Least Squares (ALS) 模型進行矩陣拆分
from pathlib import Path
from typing import Tuple, List
from io import BytesIO
import pandas as pd
import implicit
import scipy
import streamlit as st
import requests

# 取用對應資料
def load_user_artists(user_artists_file: Path) -> scipy.sparse.csr_matrix:
    """讀取檔案,並以 csr格式回傳."""
    user_artists = pd.read_csv(user_artists_file, sep="\t")
    user_artists.set_index(["userID", "artistID"], inplace=True)
    """稀疏矩陣建立"""
    coo = scipy.sparse.coo_matrix(
        (
            user_artists.weight.astype(float),
            (
                user_artists.index.get_level_values(0),
                user_artists.index.get_level_values(1),
            ),
        )
    )
    return coo.tocsr()

class ArtistRetriever:
    """從ID取得名字"""
    def __init__(self):
        self._artists_df = None

    def get_artist_name_from_id(self, artist_id: int) -> str:
        """回傳名稱"""
        return self._artists_df.loc[artist_id, "name"]

    def load_artists(self, artists_file: Path) -> None:
        """讀取檔案,使用pandas儲存."""
        artists_df = pd.read_csv(artists_file, sep="\t")
        artists_df = artists_df.set_index("id")
        self._artists_df = artists_df

class ImplicitRecommender:
    """使用implicti訓練模型
    """
    def __init__(
        self,
        artist_retriever: ArtistRetriever,
        implicit_model,
    ):
        self.artist_retriever = artist_retriever
        self.implicit_model = implicit_model

    def fit(self, user_artists_matrix: scipy.sparse.csr_matrix) -> None:
        """Fit the model to the user artists matrix."""
        self.implicit_model.fit(user_artists_matrix)

    def recommend(
        self,
        user_id: int,
        user_artists_matrix: scipy.sparse.csr_matrix,
        n: int = 10,
    ) -> Tuple[List[str], List[float]]:
        """矩陣相乘計算分數."""
        artist_ids, scores = self.implicit_model.recommend(
            user_id, user_artists_matrix[user_id], N=n
        )
        artists = [
            self.artist_retriever.get_artist_name_from_id(artist_id)
            for artist_id in artist_ids
        ]
        return artists, scores

if __name__ == "__main__":
    st.title("推薦系統結果展示")

    # 讀取資料
    user_artists = load_user_artists(Path(r"lastfmdata\user_artists.dat"))

    # instantiate artist retriever
    artist_retriever = ArtistRetriever()
    artist_retriever.load_artists(Path(r"lastfmdata\artists.dat"))

    # ALS 協同過濾算法 進行矩陣拆分
    implict_model = implicit.als.AlternatingLeastSquares(
        factors=50, iterations=10, regularization=0.01
    )

    # 訓練模型與建議
    recommender = ImplicitRecommender(artist_retriever, implict_model)
    recommender.fit(user_artists)

    # 使用者ID選擇
    with st.sidebar:
        st.header("推薦目標 & 推薦數量",divider="rainbow")
        user_id = st.selectbox("請選擇使用者ID:", options=range(1, user_artists.shape[0]+1))
        n_recommendations = st.slider("推薦數量", min_value=1, max_value=20, value=5)
        st.subheader("",divider="gray")
    if st.button("生成推薦結果"):
        artists, scores = recommender.recommend(user_id, user_artists, n=n_recommendations)
        # 在Streamlit中顯示推薦結果
        st.subheader(f"使用者 {user_id} 的推薦結果:")
        for artist, score in zip(artists, scores):
            st.write(f"{artist}: {score:.4f}")



