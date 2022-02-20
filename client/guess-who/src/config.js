let config;

if (process.env.NODE_ENV === "production") {
    config = {
        api_url: "https://api.xxx.com",
        timeoutDuration: 30000,
        someOtherProps: 'xyz'
    };
} else {
    config = {
        api_url: "http://127.0.0.1:5000",
        timeoutDuration: 1000,
    };
}

export { config }