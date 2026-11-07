import { expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Home from "../app/page";

test("renders the starter heading and documentation link", () => {
  render(<Home />);
  expect(
    screen.getByRole("heading", { level: 1, name: /to get started/i })
  ).toBeDefined();
  expect(screen.getByRole("link", { name: /documentation/i })).toBeDefined();
});