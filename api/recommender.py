import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


df = pd.read_csv('api/customer_shopping_data.csv')
df = df.iloc[:1750]


customer_data = df[['customer_id', 'product_id', 'age', ]]
product_data = df[['product_id', 'category',
                   'price', 'quantity', 'shopping_mall']]


# Splitting the data
# Split into train and test sets
train_data, test_data = train_test_split(
    customer_data, test_size=0.2, random_state=42)


# @title collaborative filtering
# Create customer-product matrix
customer_product_matrix = train_data.pivot_table(
    index='customer_id', columns='product_id', values='age')

# Fill missing values with 0
customer_product_matrix_filled = customer_product_matrix.fillna(0)

# Compute customer similarity matrix
customer_similarity = cosine_similarity(customer_product_matrix_filled)

# Function to predict ratings


def predict_ratings(customer_id, product_id):
    customer_idx = customer_product_matrix.index.get_loc(customer_id)
    if product_id in customer_product_matrix:
        product_idx = customer_product_matrix.columns.get_loc(product_id)
        weighted_sum = np.dot(
            customer_similarity[customer_idx], customer_product_matrix_filled.iloc[:, product_idx])
        sum_of_similarities = np.sum(customer_similarity[customer_idx])
        if sum_of_similarities > 0:
            return weighted_sum / sum_of_similarities
    return 0


# Content-based Filtering

# Preprocessing pipeline for product attributes
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['price']),
        ('cat', OneHotEncoder(), ['category', 'shopping_mall'])
    ]
)

# Fit the preprocessor on the product data
preprocessor.fit(product_data)

# Transform product data
product_features = preprocessor.transform(product_data)

# Compute product similarity
product_similarity = cosine_similarity(product_features)

# Function to predict ratings based on content


def predict_content_based(customer_id, product_id):
    customer_products = train_data[train_data['customer_id']
                                   == customer_id]['product_id']
    if not customer_products.empty and product_id in product_data['product_id'].values:
        product_idx = product_data[product_data['product_id']
                                   == product_id].index[0]
        customer_product_idxs = [
            product_data[product_data['product_id'] == pid].index[0] for pid in customer_products]
        similarities = product_similarity[product_idx, customer_product_idxs]
        customer_ratings = customer_product_matrix_filled.loc[customer_id,
                                                              customer_products].values
        if np.sum(similarities) > 0:
            return np.dot(similarities, customer_ratings) / np.sum(similarities)
    return 0


def hybrid_predict(customer_id, product_id, alpha=0.5):
    cf_pred = predict_ratings(customer_id, product_id)
    cb_pred = predict_content_based(customer_id, product_id)
    return alpha * cf_pred + (1 - alpha) * cb_pred

# Function to recommend top N products to a customer


def recommend_products(customer_id, top_n=5):
    product_ids = product_data['product_id'].values
    predictions = [(pid, hybrid_predict(customer_id, pid))
                   for pid in product_ids]
    # Sort by predicted rating in descending order and select top N products
    recommendations = sorted(
        predictions, key=lambda x: x[1], reverse=True)[:top_n]
    return recommendations


def recommend(customer_id, top_n=5):
    '''
    This function receives a customer's id as input and retuns the product
    id of 5 product as product recommendation to the given customer

    input:
    customer_id: str - 'C189076'

    output:
    list: ['I337046', 'I121056', 'I412481', 'I339732', 'I249424']
    '''

    rec = recommend_products(customer_id, top_n)
    recommendations = []
    for i in rec:
        recommendations.append(i[0])

    return recommendations
