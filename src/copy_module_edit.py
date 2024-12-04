def modify_index_html(self):
    new_index_html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>st-copy-to-clipboard</title>
  <script src="./streamlit-component-lib.js"></script>
  <script src="./main.js"></script>
  <style>
    /* Base styles */
    :root {
      --bg-color-light: #ffffff;
      --text-color-light: #000000;
      --bg-color-dark: #0e1117;
      --text-color-dark: #ffffff;
      --button-bg-light: #f0f2f6;
      --button-bg-dark: #262730;
      --button-border-light: #d3d3d3;
      --button-border-dark: #4a4a4a;
    }

    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
      transition: background-color 0.3s, color 0.3s;
    }

    /* Light mode (default) */
    body {
      background-color: var(--bg-color-light);
      color: var(--text-color-light);
    }

    body.dark-mode {
      background-color: var(--bg-color-dark);
      color: var(--text-color-dark);
    }

    /* Button styles */
    .st-copy-to-clipboard-btn {
      background-color: var(--button-bg-light);
      color: var(--text-color-light);
      border: 1px solid var(--button-border-light);
      padding: 8px 12px;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.3s, color 0.3s;
    }

    body.dark-mode .st-copy-to-clipboard-btn {
      background-color: var(--button-bg-dark);
      color: var(--text-color-dark);
      border-color: var(--button-border-dark);
    }

    .st-copy-to-clipboard-btn:hover {
      opacity: 0.8;
    }

    #root {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      gap: 10px;
    }
  </style>
</head>
<body>
  <div id="root">
    <button id="text-element" class="st-copy-to-clipboard-btn"></button>
    <button id="copy-button" class="st-copy-to-clipboard-btn">📋</button>
    <button id="theme-toggle" class="st-copy-to-clipboard-btn">🌓</button>
  </div>

  <script>
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // Check for saved theme preference or default to light mode
    if (localStorage.getItem('theme') === 'dark') {
      body.classList.add('dark-mode');
    }

    themeToggle.addEventListener('click', () => {
      body.classList.toggle('dark-mode');
      
      // Save theme preference
      const currentTheme = body.classList.contains('dark-mode') ? 'dark' : 'light';
      localStorage.setItem('theme', currentTheme);
      
      // Send theme change to Streamlit
      window.parent.postMessage({
        type: 'streamlit:theme',
        theme: currentTheme
      }, '*');
    });
  </script>
</body>
</html>
    """
    self.write_file(self.index_html_path, new_index_html_content.strip())