import streamlit as st
import pandas as pd
from io import StringIO

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("Daily Report (Authentic Engineers)_DAILY REPORT_Table.csv")

df = load_data()

# UI: Project Number Dropdown
st.title("📋 Daily Project Report")
project_numbers = df['Project Number'].dropna().unique()
project_numbers.sort()
selected_project_number = st.selectbox("📁 Select Project Number:", project_numbers)

# Report logic
if st.button("Generate Report"):

    filtered_df = df[df['Project Number'] == selected_project_number]

    if filtered_df.empty:
        st.error(f"No data found for Project Number: {selected_project_number}")
    else:
        # Project-level info
        project_name = filtered_df['Project Name'].iloc[0]
        unique_employee = filtered_df['Enter Your Name'].nunique()
        total_project_hours = filtered_df['Hours'].sum()
        project_dates = pd.to_datetime(filtered_df['Date'], errors='coerce').dropna()
        start_date = project_dates.min().strftime('%b %d, %Y')
        end_date = project_dates.max().strftime('%b %d, %Y')
        total_days = (project_dates.max() - project_dates.min()).days + 1
        total_departments = filtered_df['DEPARTMENT'].nunique()

        # Header display
        st.markdown("### 📌 Project Details:")
        st.text(f"Project Number      : {selected_project_number}")
        st.text(f"Project Name        : {project_name}")
        st.text(f"Number of Employees : {unique_employee}")
        st.text(f"Total Hours Spent   : {round(total_project_hours, 2)}")
        st.text(f"Start Date          : {start_date}")
        st.text(f"End Date            : {end_date}")
        st.text(f"Time Period         : {total_days} days")
        st.text(f"Departments Involved: {total_departments}")

        st.markdown("### 📊 Detailed Report:\n")

        final_output = StringIO()
        final_output.write("📌 Project Details:\n")
        final_output.write(f"Project Number      : {selected_project_number}\n")
        final_output.write(f"Project Name        : {project_name}\n")
        final_output.write(f"Number of Employees : {unique_employee}\n")
        final_output.write(f"Total Hours Spent   : {round(total_project_hours, 2)}\n")
        final_output.write(f"Start Date          : {start_date}\n")
        final_output.write(f"End Date            : {end_date}\n")
        final_output.write(f"Time Period         : {total_days} days\n")
        final_output.write(f"Departments Involved: {total_departments}\n\n")
        final_output.write("Detailed Report:\n\n")

        for dept_name, dept_df in filtered_df.groupby('DEPARTMENT'):
            unique_names = dept_df['Enter Your Name'].unique()
            total_dept_hours = dept_df['Hours'].sum()

            st.markdown(f"#### Department: {dept_name}")
            st.markdown(f"- Employees Involved: {len(unique_names)}")
            st.markdown(f"- Total Hours Spent : {round(total_dept_hours, 2)}")

            final_output.write(f"Department: {dept_name}\n")
            final_output.write(f"   - Employees Involved: {len(unique_names)}\n")
            final_output.write(f"   - Total Hours Spent : {round(total_dept_hours, 2)}\n\n")

            for name in unique_names:
                st.markdown(f"👤 **{name}**")
                person_data = dept_df[dept_df['Enter Your Name'] == name]
                daily_breakdown = person_data.groupby('Date')['Hours'].sum().reset_index()

                final_output.write(f"👤 {name}\n")

                with st.expander("📅 Show dates & hours worked"):
                    for _, row in daily_breakdown.iterrows():
                        date = row['Date']
                        hours = round(row['Hours'], 2)
                        st.markdown(f"- {date} : {hours} hours")
                        final_output.write(f"   - {date} : {hours} hours\n")
                
                final_output.write("\n")

        # Generate downloadable text file
        st.download_button(
            label="📥 Download Report (.txt)",
            data=final_output.getvalue(),
            file_name=f"{selected_project_number}_report.txt",
            mime="text/plain"
        )
