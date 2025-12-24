import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(page_title="VibeCheck | WhatsApp Analyzer", page_icon="✨", layout="wide")

st.sidebar.title("✨ VibeCheck")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("Choose a file", type=['txt', 'zip'])

if uploaded_file is None:
    st.title("Welcome to VibeCheck ✨")
    st.markdown("""
    **Ready to check the vibe of your group chat?**
    
    Upload your WhatsApp chat export to reveal:
    * 🗣️ **Who never stops talking?**
    * 😂 **Who is the Emoji Champion?**
    * 🔥 **When is the group most active?**
    
    *Your data is processed locally and never leaves your computer.*
    """)
else:
    try:
        data = ""
        if uploaded_file.name.endswith('.zip'):
            with zipfile.ZipFile(uploaded_file) as z:
                for filename in z.namelist():
                    if filename.endswith('.txt'):
                        with z.open(filename) as f:
                            data = f.read().decode("utf-8")
                        break
        else:
            data = uploaded_file.getvalue().decode("utf-8")

        df = preprocessor.preprocess(data)

        # Sidebar
        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox("Show Analysis for", user_list)
        
        if st.sidebar.button("Show Analysis"):
            
            st.title(f"Analysis: {selected_user}")
            
            # --- TOP STATISTICS ---
            num_messages, words = helper.fetch_stats(selected_user, df)
            emoji_df = helper.emoji_helper(selected_user, df)
            
            fav_emoji = "N/A"
            if not emoji_df.empty:
                fav_emoji = emoji_df.iloc[0]['emoji']

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Messages", num_messages)
            c2.metric("Total Words", words)
            c3.metric("Total Emojis", emoji_df['count'].sum() if not emoji_df.empty else 0)
            c4.metric("Favorite Emoji", fav_emoji)

            st.markdown("---")

            # --- TABS ---
            tab1, tab2, tab3, tab4 = st.tabs(["🔥 Activity Heatmap", "📈 Timeline", "👥 User Activity", "😀 Emojis"])

            # --- TAB 1: HEATMAP ---
            with tab1:
                st.subheader("Weekly Activity Map")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                
                if not user_heatmap.empty:
                    fig, ax = plt.subplots(figsize=(20, 8))
                    sns.heatmap(
                        user_heatmap, 
                        ax=ax, 
                        cmap="YlGnBu", 
                        linewidths=0.5, 
                        linecolor='white',
                        cbar_kws={'label': 'Number of Messages'}
                    )
                    plt.xlabel("Hour of Day (0-23)", fontsize=14)
                    plt.ylabel("Day of Week", fontsize=14)
                    plt.xticks(fontsize=12)
                    plt.yticks(fontsize=12, rotation=0)
                    st.pyplot(fig)
                else:
                    st.warning("Not enough data to generate a heatmap.")

            # --- TAB 2: TIMELINE ---
            with tab2:
                st.subheader("Daily Activity Timeline")
                daily_timeline = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots(figsize=(18, 5))
                ax.plot(daily_timeline['message_date'], daily_timeline['message'], color='black')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                st.markdown("---")

                # Busy Day & Busy Month Side-by-Side
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Most Busy Day")
                    busy_day = helper.week_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='purple')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                with col2:
                    st.subheader("Most Busy Month")
                    busy_month = helper.month_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='orange')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

            # --- TAB 3: USER ACTIVITY ---
            with tab3:
                if selected_user == 'Overall':
                    col1, col2 = st.columns(2)
                    
                    # 1. Most Busy Users (Messages)
                    with col1:
                        st.subheader('Most Active Users (Messages)')
                        x, new_df = helper.most_busy_users(df)
                        new_df.index = new_df.index + 1
                        
                        fig, ax = plt.subplots()
                        ax.bar(x.index, x.values, color='#FF4B4B')
                        plt.xticks(rotation='vertical')
                        st.pyplot(fig)
                        st.dataframe(new_df, use_container_width=True)

                    # 2. Emoji Leaderboard 
                    with col2:
                        st.subheader('Emoji Champions 🏆')
                        emoji_leaderboard = helper.user_emoji_leaderboard(df)
                        
                        if not emoji_leaderboard.empty:
                            emoji_leaderboard.index = emoji_leaderboard.index + 1
                            
                            # Interactive Bar Chart
                            fig = px.bar(emoji_leaderboard, x='User', y='Emojis Sent', color='Emojis Sent', title="Who uses the most emojis?")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.dataframe(emoji_leaderboard, use_container_width=True)
                        else:
                            st.write("No emojis found!")

                else:
                    st.info("Select 'Overall' to see the Leaderboards.")

            # --- TAB 4: EMOJIS ---
            with tab4:
                st.subheader("Emoji Statistics")
                if not emoji_df.empty:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        emoji_df.index = emoji_df.index + 1
                        st.dataframe(emoji_df, use_container_width=True)
                    with col2:
                        top_5 = emoji_df.head(5)
                        fig = px.pie(top_5, values='count', names='emoji', title='Top 5 Emojis')
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No emojis found!")

    except Exception as e:
        st.error(f"Error: {e}")