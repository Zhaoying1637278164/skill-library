import importlib.util
from pathlib import Path
import tempfile,unittest,zipfile

spec=importlib.util.spec_from_file_location("extract",Path(__file__).resolve().parents[1]/"tools/catalog/extract_catalog.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class ScannerTest(unittest.TestCase):
 def test_exact_skill_filename(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/"sample.zip"
   with zipfile.ZipFile(p,"w") as z:
    for name in ["SKILL.md","skills/demo/SKILL.md",".github/improve-skill.md","evals/no-skill.md"]:
     z.writestr(name,"---\nname: example\ndescription: Read transactions\n---\n# Example")
   r=module.extract(p)
   self.assertEqual([s["path"] for s in r["skills"]],["SKILL.md","skills/demo/SKILL.md"])
   self.assertIn(".github/improve-skill.md",[x["path"] for x in r.get("references",[])])
class EditorialGuardTest(unittest.TestCase):
 def setUp(self):
  spec=importlib.util.spec_from_file_location("sitebuild",Path(__file__).resolve().parents[1]/"tools/build_site.py")
  self.builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.builder)
 def test_template_and_missing_translation_are_reported(self):
  data={"records":[{"id":1,"file":"sample.zip","summary_zh":"主要用于安全检查，可查找“密钥与访问控制”相关技能或服务。具体操作范围见包内说明。","skills":[{"path":"skills/demo/SKILL.md","description":"Reads data"}]}]}
  errors=self.builder.validate_editorial(data)
  self.assertEqual(len(errors["template_summaries"]),1)
  self.assertEqual(len(errors["missing_skill_chinese"]),1)
  self.assertEqual(errors["invalid_skills"],[])
 def test_human_summary_and_translated_skill_pass(self):
  data={"records":[{"id":1,"file":"sample.zip","summary_zh":"把PDF银行流水提取为交易明细，再核对账户余额与账单期间。","skills":[{"path":"SKILL.md","description_zh":"核对账户交易和余额，输出差异清单。"}]}]}
  self.assertFalse(any(self.builder.validate_editorial(data).values()))
class PublicationNoticeTest(unittest.TestCase):
 setUp=EditorialGuardTest.setUp
 def test_partial_publication_keeps_notice_and_uses_site_asset_paths(self):
  with tempfile.TemporaryDirectory() as t:
   site=Path(t)
   errors={'template_summaries':[{}],'missing_skill_chinese':[{},{}],'invalid_skills':[]}
   self.builder.render_shell(site,False,errors,editorial_notice=True)
   html=(site/'index.html').read_text()
   self.assertIn('中文说明完善中',html)
   self.assertIn('1 个摘要与 2 条技能中文说明',html)
   self.assertIn('src="vendor/fflate.min.js"',html)
   self.assertNotIn('../site/',html)
   self.assertNotIn('本地预览',html)
   self.assertTrue((site/'topics.json').exists())

if __name__=="__main__":unittest.main()
