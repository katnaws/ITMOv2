.PHONY: install test step1 step2 step3 hooks p4-run p4-study-demo p4-dashboard p4-pack

install:
	@echo "Установка для практик 1–2 не требуется. Для практики 4:"
	@echo " - привяжите git hooks: make hooks"
	@echo " - при необходимости установите python3"

test: step1 step2 step3

step1:
	@$(MAKE) -s -C practices/practice_01 test

step2:
	@$(MAKE) -s -C practices/practice_02 test

step3:
	@$(MAKE) -s -C practices/practice_03 test

hooks:
	@chmod +x practices/practice_04/hooks/post-commit
	@git config core.hooksPath practices/practice_04/hooks
	@echo "Hooks path configured to practices/practice_04/hooks"

p4-run:
	@bash practices/practice_04/runner.sh

p4-study-demo:
	@python3 practices/practice_04/mcp/study_tracker/check.py

p4-dashboard:
	@npm --prefix practices/practice_04/dashboard run build
	@python3 practices/practice_04/dashboard/server.py

p4-pack:
	@python3 practices/practice_04/scripts/p4_report.py
	@bash practices/practice_04/runner.sh
	@python3 practices/practice_04/scripts/p4_pack.py
