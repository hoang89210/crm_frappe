#!/bin/bash
sed -n '/ERROR: test_csv_import_sample/,/^====/p' /tmp/gates.log | head -30
echo "##########"
sed -n '/ERROR: test_care_status_not_overwritten/,/^====/p' /tmp/gates.log | tail -12
