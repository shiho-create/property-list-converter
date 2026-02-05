import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Property List Converter", page_icon="🏢")

# Standard output columns
OUTPUT_COLUMNS = [
    'community_name',
    'street',
    'city',
    'state',
    'zip_code',
    'units',
    'ownership_group_name'
]

# Column mapping: maps various input column names to standard names
COLUMN_MAPPINGS = {
    'community_name': [
        'community_name', 'community', 'property_name', 'property name',
        'property', 'name', 'asset_name', 'asset name', 'project_name',
        'project name', 'complex_name', 'complex name', 'apartment_name',
        'apartment name', 'building_name', 'building name', 'community name'
    ],
    'street': [
        'street', 'address', 'street_address', 'street address',
        'address_1', 'address1', 'address 1', 'property_address',
        'property address', 'location', 'street_name', 'street name'
    ],
    'city': [
        'city', 'city_name', 'city name', 'municipality'
    ],
    'state': [
        'state', 'state_code', 'state code', 'st', 'province'
    ],
    'zip_code': [
        'zip_code', 'zip code', 'zip', 'zipcode', 'postal_code',
        'postal code', 'postalcode'
    ],
    'units': [
        'units', 'unit_count', 'unit count', 'total_units', 'total units',
        'total managed units', 'num_units', 'num units', 'number_of_units',
        'number of units', '# units', '#units', 'unit_total', 'unit total',
        'apt_count', 'apartment_count', 'doors'
    ],
    'ownership_group_name': [
        'ownership_group_name', 'ownership group name', 'ownership_group',
        'ownership group', 'owner', 'owner_name', 'owner name',
        'ownership', 'ownership name', 'management_company', 'management company',
        'management', 'company', 'company_name', 'company name',
        'landlord', 'proprietor', 'holding_company', 'holding company',
        'client', 'client_name', 'client name', 'primary_client', 'primary client',
        'primary client name', 'customer', 'customer_name', 'customer name'
    ]
}


def normalize_column_name(col_name):
    """Normalize column name for comparison."""
    return str(col_name).lower().strip()


def find_column_mapping(input_columns):
    """Find which input columns map to which output columns."""
    mapping = {}
    normalized_input = [normalize_column_name(col) for col in input_columns]

    for output_col, possible_names in COLUMN_MAPPINGS.items():
        for possible_name in possible_names:
            normalized_possible = normalize_column_name(possible_name)
            if normalized_possible in normalized_input:
                idx = normalized_input.index(normalized_possible)
                mapping[output_col] = input_columns[idx]
                break

    return mapping


def convert_dataframe(df):
    """Convert input dataframe to standardized format."""
    column_mapping = find_column_mapping(df.columns.tolist())

    result = pd.DataFrame()
    for out_col in OUTPUT_COLUMNS:
        if out_col in column_mapping:
            source_col = column_mapping[out_col]
            result[out_col] = df[source_col].astype(str).str.strip()
            result[out_col] = result[out_col].replace('nan', '')
        else:
            result[out_col] = ''

    return result, column_mapping


# App UI
st.title("Property List Converter")
st.write("Upload a property list CSV to convert it to a standardized format.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded file
    df = pd.read_csv(uploaded_file)

    st.subheader("Original File Preview")
    st.dataframe(df.head(10))

    # Convert
    converted_df, mapping = convert_dataframe(df)

    # Show mapping
    st.subheader("Column Mapping")
    mapping_display = []
    for out_col in OUTPUT_COLUMNS:
        if out_col in mapping:
            mapping_display.append(f"✅ **{out_col}** ← _{mapping[out_col]}_")
        else:
            mapping_display.append(f"⚠️ **{out_col}** ← _not found (will be empty)_")

    for item in mapping_display:
        st.markdown(item)

    # Show converted preview
    st.subheader("Converted File Preview")
    st.dataframe(converted_df.head(10))

    st.write(f"**Total rows:** {len(converted_df)}")

    # Download button
    csv_buffer = io.StringIO()
    converted_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    original_name = uploaded_file.name.replace('.csv', '')

    st.download_button(
        label="Download Converted CSV",
        data=csv_data,
        file_name=f"{original_name}_converted.csv",
        mime="text/csv"
    )
