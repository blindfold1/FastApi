const searchAndAddFood = async () => {
    let accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        setError('No access token found. Please login again.');
        navigate('/');
        return;
    }

    try {
        const response = await axios.post(
            'http://127.0.0.1:8000/food/search-and-add-food/', // Fix the URL
            { name: productName, exact_match: false, data_type: "Foundation" }, // Match the expected payload
            {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            }
        );
        setAddedFood(response.data);
        setProductName(''); // Очищаем поле ввода
    } catch (err) {
        console.error("Error in searchAndAddFood:", err);
        console.error("Error message:", err.message);
        console.error("Error response:", err.response);
        console.error("Error request:", err.request);
        console.error("Error config:", err.config);
        if (err.response?.status === 401) {
            accessToken = await refreshAccessToken();
            if (accessToken) {
                try {
                    const response = await axios.post(
                        'http://127.0.0.1:8000/food/search-and-add-food/',
                        { name: productName, exact_match: false, data_type: "Foundation" },
                        {
                            headers: {
                                Authorization: `Bearer ${accessToken}`,
                                'Content-Type': 'application/json',
                            },
                        }
                    );
                    setAddedFood(response.data);
                    setProductName('');
                } catch (retryErr) {
                    console.error("Retry error:", retryErr);
                    setError('Failed to add food: ' + (retryErr.response?.data?.detail || retryErr.message));
                }
            }
        } else {
            setError('Failed to add food: ' + (err.response?.data?.detail || err.message));
        }
    }
};