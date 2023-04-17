# SnowAI: Simple Data Querying and Visualization with Snowflake, Streamlit, and ChatGPT

SnowAI is a friendly data querying and visualization tool, perfect for those without SQL or Snowflake experience. 🎉 

### How does it work? 🤔

Just type your question in a text box, and SnowAI will handle the rest. It knows your Snowflake Data Sources and presents the results as a table or visualization, complete with a custom title.

No need to know SQL or Data Sources schema 🧳.

### Give it a try! 🚀
1. Get an OpenAI account and a generated key.
2. Set up a Snowflake Account and a SnowAI user/role. Grant required permissions (see database/setup.sql file).
3. Copy `.env.default` and fill it with your credentials.
4. Run source `init.sh`.
5. Launch `streamlit run main_streamlit.py`.

### What's inside? 📦
- An interactive web app powered by Streamlit.
- Snowpark integration.
- ChatGPT integration 3.5 (version 4 coming soon).

### Upcoming Features 🌟
- Auto-select chart type with a label.
- Validate SQL query syntax before sending it to Snowflake.
- Train GPT to recommend the best chart to use.
- Implement support for custom LLMs (Large Language Models).
- Multiple export options for sharing insights.
- Integrations.
- Connectors.

And much more! 💡
