import os
import unittest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDONS_DIR = os.path.join(REPO_ROOT, "addons")

EXPECTED_ADDONS = [
    "uptime",
    "telegram_bridge",
    "webpreview",
    "bouncer",
    "ntfy",
    "yt",
    "username",
    "publish",
]

class TestRepositoryStructure(unittest.TestCase):
    def test_repository_yaml(self):
        repo_yaml_path = os.path.join(REPO_ROOT, "repository.yaml")
        self.assertTrue(os.path.isfile(repo_yaml_path), "repository.yaml must exist at repo root")
        
        with open(repo_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        self.assertIsInstance(data, dict)
        self.assertIn("name", data)
        self.assertIn("url", data)
        self.assertIn("maintainer", data)
        self.assertEqual(data["maintainer"], "Gluek <gluek@gluek.info>")

    def test_repository_icon(self):
        icon_path = os.path.join(REPO_ROOT, "icon.png")
        self.assertTrue(os.path.isfile(icon_path), "icon.png must exist at repo root")
        self.assertGreater(os.path.getsize(icon_path), 100, "icon.png must not be empty")

    def test_addons_exist(self):
        self.assertTrue(os.path.isdir(ADDONS_DIR), "addons/ directory must exist")
        for addon in EXPECTED_ADDONS:
            addon_path = os.path.join(ADDONS_DIR, addon)
            self.assertTrue(os.path.isdir(addon_path), f"Addon directory {addon} must exist")

    def test_addons_files_and_configs(self):
        for addon in EXPECTED_ADDONS:
            addon_path = os.path.join(ADDONS_DIR, addon)
            with self.subTest(addon=addon):
                # Check config.yaml
                config_path = os.path.join(addon_path, "config.yaml")
                self.assertTrue(os.path.isfile(config_path), f"{addon}/config.yaml must exist")
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                
                self.assertIsInstance(config, dict)
                self.assertIn("name", config)
                self.assertIn("version", config)
                self.assertIn("slug", config)
                self.assertIn("description", config)
                self.assertIn("arch", config)
                self.assertIsInstance(config["arch"], list)
                self.assertIn("amd64", config["arch"])
                self.assertIn("aarch64", config["arch"])
                self.assertIn("image", config)
                self.assertTrue(config["image"].startswith("ghcr.io/mrgluek/addon-deltachat-"))
                
                # Check options and schema
                self.assertIn("schema", config)
                self.assertIn("options", config)

                # Check Dockerfile
                dockerfile_path = os.path.join(addon_path, "Dockerfile")
                self.assertTrue(os.path.isfile(dockerfile_path), f"{addon}/Dockerfile must exist")
                with open(dockerfile_path, "r", encoding="utf-8") as f:
                    df_content = f.read()
                self.assertIn("FROM", df_content)
                self.assertIn("git clone", df_content)
                self.assertIn("git.gluek.info", df_content, f"{addon}/Dockerfile must include Forgejo backup fallback")

                # Check run.sh is executable
                run_sh_path = os.path.join(addon_path, "run.sh")
                self.assertTrue(os.path.isfile(run_sh_path), f"{addon}/run.sh must exist")
                self.assertTrue(os.access(run_sh_path, os.X_OK), f"{addon}/run.sh must be executable")
                with open(run_sh_path, "r", encoding="utf-8") as f:
                    sh_content = f.read()
                self.assertTrue(sh_content.startswith("#!/"), f"{addon}/run.sh must start with shebang")

                # Check DOCS.md & CHANGELOG.md
                docs_path = os.path.join(addon_path, "DOCS.md")
                self.assertTrue(os.path.isfile(docs_path), f"{addon}/DOCS.md must exist")
                changelog_path = os.path.join(addon_path, "CHANGELOG.md")
                self.assertTrue(os.path.isfile(changelog_path), f"{addon}/CHANGELOG.md must exist")

                # Check icon.png
                icon_path = os.path.join(addon_path, "icon.png")
                self.assertTrue(os.path.isfile(icon_path), f"{addon}/icon.png must exist")

                # Check translations
                en_trans_path = os.path.join(addon_path, "translations", "en.yaml")
                self.assertTrue(os.path.isfile(en_trans_path), f"{addon}/translations/en.yaml must exist")
                with open(en_trans_path, "r", encoding="utf-8") as f:
                    en_trans = yaml.safe_load(f)
                self.assertIn("configuration", en_trans)

                ru_trans_path = os.path.join(addon_path, "translations", "ru.yaml")
                self.assertTrue(os.path.isfile(ru_trans_path), f"{addon}/translations/ru.yaml must exist")
                with open(ru_trans_path, "r", encoding="utf-8") as f:
                    ru_trans = yaml.safe_load(f)
                self.assertIn("configuration", ru_trans)

                # Verify all options in config.yaml have translations in en and ru
                for opt_key in config.get("options", {}):
                    self.assertIn(opt_key, en_trans["configuration"], f"{addon}: Option '{opt_key}' missing in en.yaml")
                    self.assertIn(opt_key, ru_trans["configuration"], f"{addon}: Option '{opt_key}' missing in ru.yaml")

if __name__ == "__main__":
    unittest.main()
