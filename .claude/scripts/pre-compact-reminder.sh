#!/bin/bash
# RaiSE Pre-Compact Memory Reminder
# Called before context compaction to remind about memory preservation

echo ""
echo "---"
echo "## ⚠️ Context Compaction Approaching"
echo ""
echo "Before context is summarized, consider saving:"
echo ""
echo "- **Patterns discovered** → \`raise memory add-pattern \"description\" -c \"context,keywords\"\`"
echo "- **Calibration data** → \`raise memory add-calibration FEATURE \"Name\" SIZE ACTUAL_MIN\`"
echo "- **Session summary** → \`raise memory add-session \"topic\" -o \"outcome1,outcome2\"\`"
echo ""
echo "Or run **/session-close** for guided memory update."
echo "---"
echo ""
