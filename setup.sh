mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
[theme]\n\
primaryColor = '#ff0000'\n\
backgroundColor = '#00172b'\n\
secondaryBackgroundColor = '#4b77be'
textColor = '#ffffff'\n\
font = 'sans serif'\n\
" > ~/.streamlit/config.toml