import argparse
import json
import sys
from datetime import datetime, timezone

import boto3

from constants import (
    EBS_GP3_COST_PER_GB,
    T3_MICRO_MONTHLY,
    ELASTIC_IP_MONTHLY,
    REQUIRED_TAGS
)

ec2 = boto3.client(
    "ec2",
    region_name="us-east-1",
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

findings = []


def get_tag_dict(tags):
    if not tags:
        return {}

    return {tag["Key"]: tag["Value"] for tag in tags}


def has_required_tags(tags):
    return all(tag in tags for tag in REQUIRED_TAGS)


def scan_ebs_orphans():
    response = ec2.describe_volumes()

    for volume in response["Volumes"]:
        if volume["State"] == "available":
            tags = get_tag_dict(volume.get("Tags", []))

            findings.append({
                "resource_id": volume["VolumeId"],
                "resource_type": "ebs_volume",
                "reason": "unattached",
                "age_days": 0,
                "estimated_monthly_cost_usd": volume["Size"] * EBS_GP3_COST_PER_GB,
                "tags": tags,
                "suggested_action": "delete",
                "safe_to_auto_delete": tags.get("Protected") != "true"
            })


def scan_stopped_instances(days=14):
    response = ec2.describe_instances()

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            state = instance["State"]["Name"]

            if state == "stopped":
                tags = get_tag_dict(instance.get("Tags", []))

                findings.append({
                    "resource_id": instance["InstanceId"],
                    "resource_type": "ec2_instance",
                    "reason": f"stopped_for_more_than_{days}_days",
                    "age_days": days,
                    "estimated_monthly_cost_usd": T3_MICRO_MONTHLY,
                    "tags": tags,
                    "suggested_action": "terminate",
                    "safe_to_auto_delete": tags.get("Protected") != "true"
                })


def scan_unused_eips():
    response = ec2.describe_addresses()

    for address in response["Addresses"]:
        if "AssociationId" not in address:
            findings.append({
                "resource_id": address["AllocationId"],
                "resource_type": "elastic_ip",
                "reason": "unassociated",
                "age_days": 0,
                "estimated_monthly_cost_usd": ELASTIC_IP_MONTHLY,
                "tags": {},
                "suggested_action": "release",
                "safe_to_auto_delete": True
            })


def scan_missing_tags():
    response = ec2.describe_volumes()

    for volume in response["Volumes"]:
        tags = get_tag_dict(volume.get("Tags", []))

        if not has_required_tags(tags):
            findings.append({
                "resource_id": volume["VolumeId"],
                "resource_type": "ebs_volume",
                "reason": "missing_required_tags",
                "age_days": 0,
                "estimated_monthly_cost_usd": 0,
                "tags": tags,
                "suggested_action": "tag_resource",
                "safe_to_auto_delete": False
            })


def generate_report():
    total_waste = sum(
        finding["estimated_monthly_cost_usd"]
        for finding in findings
    )

    report = {
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "account_id": "000000000000",
        "region": "us-east-1",
        "summary": {
            "total_orphans": len(findings),
            "estimated_monthly_waste_usd": round(total_waste, 2)
        },
        "findings": findings
    }

    with open("report.json", "w") as file:
        json.dump(report, file, indent=2)

    return report


def generate_markdown(report):
    lines = [
        "# Cost Janitor Report",
        "",
        f"Total findings: {report['summary']['total_orphans']}",
        f"Estimated monthly waste: ${report['summary']['estimated_monthly_waste_usd']}",
        ""
    ]

    for finding in report["findings"]:
        lines.extend([
            f"## {finding['resource_id']}",
            f"- Type: {finding['resource_type']}",
            f"- Reason: {finding['reason']}",
            f"- Suggested Action: {finding['suggested_action']}",
            ""
        ])

    with open("report.md", "w") as file:
        file.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True
    )

    parser.add_argument(
        "--delete",
        action="store_true"
    )

    args = parser.parse_args()

    scan_ebs_orphans()
    scan_stopped_instances()
    scan_unused_eips()
    scan_missing_tags()

    report = generate_report()

    generate_markdown(report)

    if args.dry_run and findings:
        sys.exit(1)


if __name__ == "__main__":
    main()