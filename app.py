import streamlit as st
import pandas as pd

# Load your dataset
@st.cache_data
def load_data():
    return pd.read_csv("Daily Report (Authentic Engineers)_DAILY REPORT_Table.csv")  # Change this if your file name is different

df = load_data()

st.set_page_config(page_title="Project Report Viewer", layout="wide")
st.title("📊 Project Report Viewer")

project_number_input = st.text_input("Enter Project Number:")

if project_number_input:
    filtered_df = df[df['Project Number'] == project_number_input.strip()]

    if filtered_df.empty:
        st.warning("❌ No data found for this project number.")
    else:
        # Project Summary Info
        project_name = filtered_df['Project Name'].iloc[0]
        unique_employee = filtered_df['Enter Your Name'].nunique()
        total_project_hours = filtered_df['Hours'].sum()
        project_dates = pd.to_datetime(filtered_df['Date'], errors='coerce').dropna()
        start_date = project_dates.min().strftime('%b %d, %Y')
        end_date = project_dates.max().strftime('%b %d, %Y')
        total_days = (project_dates.max() - project_dates.min()).days + 1
        total_departments = filtered_df['DEPARTMENT'].nunique()

        # Display on screen
        st.markdown(f"""
        ### 📌 Project Details:
        - **Project Number**: {project_number_input}
        - **Project Name**: {project_name}
        - **Number of Employees**: {unique_employee}
        - **Total Hours Spent**: {round(total_project_hours, 2)}
        - **Start Date**: {start_date}
        - **End Date**: {end_date}
        - **Time Period**: {total_days} days
        - **Departments Involved**: {total_departments}
        """)

        st.markdown("---")
        st.markdown("### 🧾 Detailed Report:")

        # Text report string
        summary_text = f"""
📌 Project Details:
Project Number      : {project_number_input}
Project Name        : {project_name}
Number of Employees : {unique_employee}
Total Hours Spent   : {round(total_project_hours, 2)}
Start Date          : {start_date}
End Date            : {end_date}
Time Period         : {total_days} days
Departments Involved: {total_departments}

Detailed Report:
"""

        department_groups = filtered_df.groupby('DEPARTMENT')

        for dept_name, dept_df in department_groups:
            unique_names = dept_df['Enter Your Name'].unique()
            total_dept_hours = dept_df['Hours'].sum()

            # Show department info on screen
            st.markdown(f"#### 📁 Department: {dept_name}")
            st.markdown(f"- Employees Involved: **{len(unique_names)}**")
            st.markdown(f"- Total Hours Spent: **{round(total_dept_hours, 2)}**")

            # Add to txt report
            summary_text += f"\nDepartment: {dept_name}\n"
            summary_text += f"   - Employees Involved: {len(unique_names)}\n"
            summary_text += f"   - Total Hours Spent : {round(total_dept_hours, 2)}\n"

            for name in unique_names:
                person_data = dept_df[dept_df['Enter Your Name'] == name]
                daily = person_data.groupby('Date')['Hours'].sum().reset_index()

                # On-screen report
                st.markdown(f"👤 **{name}**")
                with st.expander(f"📅 Show dates & hours for {name}"):
                    for _, row in daily.iterrows():
                        st.markdown(f"- `{row['Date']}` : **{round(row['Hours'], 2)} hours**")

                # Add to txt report
                summary_text += f"\n👤 {name}\n"
                for _, row in daily.iterrows():
                    summary_text += f"   - {row['Date']} : {round(row['Hours'], 2)} hours\n"

            st.markdown("---")

        # Final download button (TXT only)
        st.markdown("## 📄 Download Summary Report")
        st.download_button(
            label="📄 Download Summary Report (TXT)",
            data=summary_text,
            file_name=f"{project_number_input}_summary.txt",
            mime='text/plain'
        )
