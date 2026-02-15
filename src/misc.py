import random

class Misc:
    @staticmethod
    def loaderx():
        n = random.randint(0,2)
        loader = ["🔄 Loading... Hold on tight!","⏳ AI is brewing your content potion...","🌟 The AI is working its magic...","🤖 Processing your request... AI at work!",]
        return n,loader


    @staticmethod
    def footer():
        ft = """
        <style>
        a:link , a:visited{
        color: #BFBFBF;
        background-color: transparent;
        text-decoration: none;
        }

        a:hover,  a:active {
        color: #0283C3;
        background-color: transparent;
        text-decoration: underline;
        }

        #page-container {
        position: relative;
        min-height: 10vh;
        }

        footer{
            visibility:hidden;
        }

        .footer {
        position: relative;
        left: 0;
        top:-25px;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: #808080;
        text-align: left;
        }
        </style>

        <div id="page-container">

        <div class="footer">
        <p style='font-size: 0.875em;'><a style='display: inline; text-align: left;'></a><br 'style= top:3px;'>
        By <a style='display: inline; text-align: left;' href="" target="https://github.com/Rajendra0309">Rajendra⚡</a></p>
        </div>

        </div>
        """
        return ft
