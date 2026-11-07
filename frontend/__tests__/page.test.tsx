import { expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import RootPage from "../app/(default)/page";

test("root page links to the default locale", () => {
  render(<RootPage />);
  const link = screen.getByRole("link", { name: /przejdź do aplikacji/i });
  expect(link.getAttribute("href")).toBe("/pl");
});