"""SmartFin Agri Streamlit dashboard."""

from pathlib import Path

import streamlit as st

from SmartFin_Console_Agricultural import DEFAULT_DATABASE, SmartFinStore


st.set_page_config(
    page_title="SmartFin Agri",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_store(database_path: str) -> SmartFinStore:
    return SmartFinStore(database_path)


def format_fcfa(amount: float) -> str:
    return f"{amount:,.0f} FCFA".replace(",", " ")


def main() -> None:
    st.title("🌾 SmartFin Agri")
    st.caption("Console de gestion financière et agricole pour petites exploitations")

    with st.sidebar:
        st.header("Configuration")
        database = st.text_input("Base SQLite", str(DEFAULT_DATABASE))
        st.info(
            "Les données sont stockées localement. Le score est indicatif et "
            "ne remplace pas une décision de crédit."
        )

    store = get_store(str(Path(database).expanduser()))
    report = store.report()

    metric_columns = st.columns(4)
    metric_columns[0].metric("Revenus", format_fcfa(report.income))
    metric_columns[1].metric("Dépenses", format_fcfa(report.expenses))
    metric_columns[2].metric("Résultat net", format_fcfa(report.net_profit))
    metric_columns[3].metric("Score", f"{report.credit_score}/100")

    left, right = st.columns(2)
    with left:
        st.subheader("📦 Stock disponible")
        if report.inventory:
            st.bar_chart(report.inventory, y_label="Kilogrammes")
        else:
            st.info("Aucune récolte enregistrée.")
    with right:
        st.subheader("💰 Répartition financière")
        st.bar_chart(
            {"Revenus": report.income, "Dépenses": report.expenses},
            y_label="FCFA",
        )

    st.divider()
    form_left, form_right = st.columns(2)
    with form_left:
        st.subheader("Ajouter une récolte")
        with st.form("harvest_form", clear_on_submit=True):
            crop = st.text_input("Culture", placeholder="Oignons")
            quantity = st.number_input("Quantité (kg)", min_value=0.01, step=1.0)
            submitted = st.form_submit_button("Enregistrer la récolte")
            if submitted:
                try:
                    store.add_harvest(crop, quantity)
                    st.success("Récolte enregistrée.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    with form_right:
        st.subheader("Ajouter une transaction")
        with st.form("transaction_form", clear_on_submit=True):
            transaction_type = st.selectbox(
                "Type", options=["income", "expense"], format_func=lambda value: {
                    "income": "Revenu",
                    "expense": "Dépense",
                }[value]
            )
            amount = st.number_input("Montant (FCFA)", min_value=0.01, step=1000.0)
            description = st.text_input("Description", placeholder="Vente de tomates")
            submitted = st.form_submit_button("Enregistrer la transaction")
            if submitted:
                try:
                    store.add_transaction(transaction_type, amount, description)
                    st.success("Transaction enregistrée.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    st.divider()
    st.subheader("Historique récent")
    transactions = store.transactions()
    if transactions:
        rows = [
            {
                "Date": str(transaction["created_at"])[:19].replace("T", " "),
                "Type": "Revenu"
                if transaction["transaction_type"] == "income"
                else "Dépense",
                "Montant": format_fcfa(float(transaction["amount_fcfa"])),
                "Description": transaction["description"],
            }
            for transaction in transactions
        ]
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.info("Aucune transaction enregistrée.")


if __name__ == "__main__":
    main()
