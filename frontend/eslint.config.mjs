import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      // O'zbek tilida apostrof alifboning bir qismi: o'yin, so'nggi, g'alaba.
      // Har birini &apos; ga aylantirish matnni o'qib bo'lmas holga keltiradi,
      // JSX esa apostrofni to'g'ri chiqaradi — qoida bu yerda foyda bermaydi.
      "react/no-unescaped-entities": "off",
      // catch (err) blokida xatoni ishlatmaslik odatiy hol
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", caughtErrors: "none" },
      ],
    },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
