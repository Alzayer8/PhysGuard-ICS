# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

"""Upload-first Example Workspace for the PhysGuard-ICS public release."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from physguard.config import load_config  # noqa: E402
from physguard.experiments import run_experiment  # noqa: E402

st.set_page_config(page_title="PhysGuard-ICS Example Workspace", page_icon="🛡️", layout="wide")


def _load_upload(upload: object) -> pd.DataFrame:
    return pd.read_csv(upload)  # type: ignore[arg-type]


def main() -> None:
    """Render the public, synthetic-data-first dashboard."""

    st.image(str(ROOT / "assets" / "banner.png"), use_container_width=True)
    st.title("PhysGuard-ICS Example Workspace")
    st.caption("Offline, physics-aware telemetry triage — public release v1.0.0")
    st.info(
        "Use synthetic or authorized local telemetry only. This demonstration does not connect "
        "to industrial systems and its output is not an operational safety determination."
    )

    with st.sidebar:
        st.image(str(ROOT / "assets" / "logo.png"), width=112)
        st.header("Workspace")
        workspace_text = st.text_input(
            "Experiment root",
            value=str(ROOT / "example-workspace"),
            help="Each run creates a unique child under experiments/. Existing runs are never replaced.",
        )
        st.markdown(
            "[Dataset guide]"
            "(https://github.com/Alzayer8/PhysGuard-ICS/blob/main/docs/DATASET_GUIDE.md)"
        )

    st.subheader("1. Upload chronological CSV splits")
    columns = st.columns(3)
    train_upload = columns[0].file_uploader("train.csv", type="csv")
    validation_upload = columns[1].file_uploader("validation.csv", type="csv")
    test_upload = columns[2].file_uploader("test.csv", type="csv")
    ready = all(upload is not None for upload in (train_upload, validation_upload, test_upload))

    st.subheader("2. Create a new experiment")
    if st.button("Analyze uploaded data", type="primary", disabled=not ready):
        try:
            with st.spinner("Validating and analyzing..."):
                destination = run_experiment(
                    train=_load_upload(train_upload),
                    validation=_load_upload(validation_upload),
                    test=_load_upload(test_upload),
                    workspace=Path(workspace_text).expanduser(),
                    config=load_config(ROOT / "configs" / "example.yaml"),
                )
            st.session_state["latest_experiment"] = str(destination)
        except Exception as error:
            st.error(f"Analysis stopped safely: {error}")

    latest = st.session_state.get("latest_experiment")
    if not latest:
        st.caption("Try the files in sample_data/ to explore the complete flow.")
        return

    destination = Path(latest)
    summary_path = destination / "outputs" / "summary.json"
    analysis_path = destination / "outputs" / "analysis.csv"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    analysis = pd.read_csv(analysis_path)
    run_summary = summary["summary"]

    st.success(f"Created {summary['experiment_id']}")
    metric_columns = st.columns(3)
    metric_columns[0].metric("Rows analyzed", run_summary["rows"])
    metric_columns[1].metric("Alert rows", run_summary["alerts"])
    metric_columns[2].metric("Maximum anomaly score", f"{run_summary['max_anomaly_score']:.2f}")

    figure = px.line(
        analysis,
        x="timestamp",
        y="anomaly_score",
        color="fusion_category",
        title="Anomaly score and retained fusion evidence",
        markers=True,
    )
    st.plotly_chart(figure, use_container_width=True)
    st.dataframe(
        analysis[["timestamp", "anomaly_score", "physics_reasons", "fusion_category"]],
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download analysis.csv",
        data=analysis_path.read_bytes(),
        file_name=f"{summary['experiment_id']}-analysis.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
