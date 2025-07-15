import streamlit as st
import pandas as pd
from io import StringIO

# Load CSV
@st.cache_data
def load_data():
    return pd.read_csv("Daily Report (Authentic Engineers)_DAILY REPORT_Table.csv")

df = load_data()

# App Title
st.title("📋 Daily Project Report")

# Search Input (Project Number or Name)
st.markdown("## 🔍 Search & Select Project")
search_text = st.text_input("Enter part of the project number or project name (e.g., 23-1037 or EOL BARCODE):")

# Filter by project number OR project name
matches = df[
    df['Project Number'].astype(str).str.contains(search_text, case=False, na=False) |
    df['Project Name'].astype(str).str.contains(search_text, case=False, na=False)
]

if not matches.empty:
    # Combine number and name for user-friendly display
    matches['Label'] = matches['Project Number'] + " - " + matches['Project Name']
    selected_label = st.selectbox("📁 Matching Projects:", sorted(matches['Label'].unique()))
    selected_project_number = selected_label.split(" - ")[0]

    if st.button("Generate Report"):

        filtered_df = df[df['Project Number'] == selected_project_number]

        if filtered_df.empty:
            st.error(f"No data found for Project Number: {selected_project_number}")
        else:
            # Project Summary
            project_name = filtered_df['Project Name'].iloc[0]
            unique_employee = filtered_df['Enter Your Name'].nunique()
            total_project_hours = filtered_df['Hours'].sum()
            project_dates = pd.to_datetime(filtered_df['Date'], errors='coerce').dropna()
            start_date = project_dates.min().strftime('%b %d, %Y')
            end_date = project_dates.max().strftime('%b %d, %Y')
            total_days = (project_dates.max() - project_dates.min()).days + 1
            total_departments = filtered_df['DEPARTMENT'].nunique()

            # Display Project Summary
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

            # Group by Department
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
                    person_data = dept_df[dept_df['Enter Your Name'] == name]
                    daily_breakdown = person_data.groupby('Date')['Hours'].sum().reset_index()

                    st.markdown(f"👤 **{name}**")
                    final_output.write(f"👤 {name}\n")

                    with st.expander("📅 Show dates & hours worked", expanded=False):
                        for _, row in daily_breakdown.iterrows():
                            date = row['Date']
                            hours = round(row['Hours'], 2)
                            st.markdown(f"- {date} : {hours} hours")
                            final_output.write(f"   - {date} : {hours} hours\n")

                    final_output.write("\n")

            # Download TXT Report
            st.download_button(
                label="📥 Download Report (.txt)",
                data=final_output.getvalue(),
                file_name=f"{selected_project_number}_report.txt",
                mime="text/plain"
            )

else:
    st.info("Start typing a project number or name to view and generate its report.")
